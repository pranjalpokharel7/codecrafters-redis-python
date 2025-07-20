from dataclasses import dataclass
from enum import IntEnum

from app.storage.rdb.errors import (
    InvalidMagicByte,
    InvalidVersionNumber,
    UnknownEncoding,
)
from app.storage.types import RDBReader, RedisEncoding, RedisValue


@dataclass
class ParsedRDB:
    version: int  # redis version that created this file
    aux: dict  # auxiliary field key-value pairs
    db: dict[bytes, RedisValue]  # actual key-value pairs stored as per user commands
    selectdb: int | None  # selected db number
    checksum: bytes  # file checksum in bytes
    db_ht_size: int | None = None  # size of the database hash table (if available)
    exp_ht_size: int | None = None  # size of the expiry hash table (if available)


class LengthEncodingType(IntEnum):
    """Flag that indicates the type of length encoding:

    1. Length prefixed strings
    2. An 8, 16 or 32 bit integer
    3. A LZF compressed string

    Based on the encoding type, the length encoded bytes can be further decoded.
    """

    STRING = 0
    INTEGER = 1
    COMPRESSED = 2


class RDBParser:
    """Parses and RDB file and extracts relevant information from it."""

    version: int  # redis version that created this file
    aux: dict  # auxiliary field key-value pairs
    selectdb: int | None  # db selected
    db_ht_size: int | None = None  # size of the database hash table (if available)
    exp_ht_size: int | None = None  # size of the expiry hash table (if available)
    db: dict[bytes, RedisValue]  # actual key-value pairs stored as per user commands
    checksum: bytes  # file checksum in bytes

    def parse(self, reader: RDBReader) -> ParsedRDB:
        """Parse binary RDB file to a structured ParsedRDB object."""
        aux = {}
        db = {}
        selectdb = None
        db_ht_size = None
        exp_ht_size = None
        checksum = b""

        version = self._parse_header(reader)

        # parse until EOF is reached
        while True:
            opcode = reader.read(1)[0]
            match opcode:
                case 0xFA:
                    key, value = self._parse_auxiliary_field(reader)
                    aux[key] = value
                case 0xFE:
                    selectdb = self._parse_select_db(reader)
                case 0xFB:
                    db_ht_size, exp_ht_size = self._parse_resize_db(reader)
                case 0xFD:
                    expiry = int.from_bytes(reader.read(4), "little") * 1000  # ms
                    key, value = self._parse_key_value(reader, expiry)
                    db[key] = value
                case 0xFC:
                    expiry = int.from_bytes(reader.read(8), "little")
                    key, value = self._parse_key_value(reader, expiry)
                    db[key] = value
                case 0xFF:
                    checksum = reader.read(8)
                    break  # EOF
                case _:
                    # default case is to parse key-value pair
                    # opcode is the value type in this case
                    reader.seek(reader.tell() - 1)
                    key, value = self._parse_key_value(reader)
                    db[key] = value

        return ParsedRDB(
            version=version,
            db=db,
            aux=aux,
            selectdb=selectdb,
            db_ht_size=db_ht_size,
            exp_ht_size=exp_ht_size,
            checksum=checksum,
        )

    def _read_length_encoded_bytes(
        self, reader: RDBReader
    ) -> tuple[bytes, LengthEncodingType]:
        """Read the following bytes encoded in length encoding.

        This method also returns the LengthEncodingType as the second
        part of the tuple. This is provided so that further decoding of
        the bytes can be done on the calling site as necessary. This
        method only handles retrieving of relevant bytes.
        """
        first_byte = reader.read(1)[0]
        prefix = first_byte >> 6  # get 2 MSbs
        suffix = first_byte & 0x3F  # the remaining 6 bits

        # At a high level, length encoding works by,
        # 1. Read one byte from stream
        # 2. Compare two most significant bits (MSbs)
        # 3. Parse length and read into the stream
        if prefix == 0b00:
            length = suffix
        elif prefix == 0b01:
            length = suffix << 8 | reader.read(1)[0]
        elif prefix == 0b10:
            length = int.from_bytes(reader.read(4), "little")
        else:
            if suffix == 0:
                return reader.read(1), LengthEncodingType.INTEGER
            elif suffix == 1:
                return reader.read(2), LengthEncodingType.INTEGER
            elif suffix == 2:
                return reader.read(4), LengthEncodingType.INTEGER
            elif suffix == 3:
                raise NotImplementedError(
                    "decoding compressed strings not supported (yet)"
                )
            else:
                raise UnknownEncoding(
                    "tried to parse bytes which is not length encoded"
                )

        return reader.read(length), LengthEncodingType.STRING

    def _parse_header(self, reader: RDBReader) -> int:
        """Parses the header section of the RDB file and moves file pointer to
        the end of the header."""
        reader.seek(0)  # start from the beginning of the buffer

        # read magic bytes and validate
        magic_bytes = reader.read(5)
        if magic_bytes != b"REDIS":
            raise InvalidMagicByte(magic_bytes)

        # read version
        version = reader.read(4)
        try:
            version = int(version.decode())  # read the version number
        except (UnicodeDecodeError, ValueError):
            raise InvalidVersionNumber(version)

        return version

    def _parse_key_value(
        self, reader: RDBReader, expiry: int | None = None
    ) -> tuple[bytes, RedisValue]:
        """Parse key-value pair with optional expiry timestamp."""
        encoding = int.from_bytes(reader.read(1), "little")
        try:
            encoding = RedisEncoding(encoding)
        except ValueError:
            raise UnknownEncoding(f"{encoding} is not a valid value type")

        key = self._read_length_encoded_bytes(reader)[0]
        value_raw_bytes, _ = self._read_length_encoded_bytes(reader)
        return key, RedisValue(
            expiry=expiry, raw_bytes=value_raw_bytes, encoding=encoding
        )

    def _parse_auxiliary_field(self, reader: RDBReader) -> tuple[bytes, bytes]:
        """Parse auxiliary field key-values."""
        k = self._read_length_encoded_bytes(reader)[0]
        v, _ = self._read_length_encoded_bytes(reader)
        return k, v

    def _parse_select_db(self, reader: RDBReader) -> int:
        """This function parses information specific to selecting database.

        A Redis instance can have multiple databases. A single byte 0xFE
        flags the start of the database selector. After this byte, a
        variable length field indicates the database number.
        """
        db_number, _ = self._read_length_encoded_bytes(reader)
        return int.from_bytes(db_number, "little")

    def _parse_resize_db(self, reader: RDBReader) -> tuple[int, int]:
        """Parses resizedb information, which contains information about size
        of the hash table for the main keyspace and expires."""
        db_ht_size = int.from_bytes(reader.read(1), "little")
        exp_ht_size = int.from_bytes(reader.read(1), "little")
        return db_ht_size, exp_ht_size
