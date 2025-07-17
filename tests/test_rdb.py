from io import BytesIO
from os import read
from app.storage.rdb.parser import RDBParser, RDBReader
from app.storage.rdb.errors import InvalidMagicByte, InvalidVersionNumber
from app.storage.base import RedisEncoding


def get_rdb_reader(version=b"0003", body=b"", checksum=b"\x00" * 8) -> RDBReader:
    buffer = b"REDIS" + version + body + b"\xff" + checksum
    return BytesIO(buffer)


def test_valid_header_parsing():
    parser = RDBParser(get_rdb_reader())
    assert parser.version == 3


def test_invalid_magic_byte():
    try:
        RDBParser(BytesIO(b"WRONG0003\xff" + b"\x00" * 8))
        assert False, "Expected InvalidMagicByte"
    except InvalidMagicByte:
        pass


def test_invalid_version_number():
    try:
        RDBParser(BytesIO(b"REDISbad!" + b"\xff" + b"\x00" * 8))
        assert False, "Expected InvalidVersionNumber"
    except InvalidVersionNumber:
        pass


def test_aux_field_parsing():
    body = b"\xfa" + b"\x01k" + b"\x01v"
    parser = RDBParser(get_rdb_reader(body=body))
    assert parser.aux[b"k"] == b"v"


def test_select_db():
    body = b"\xfe" + b"\x01\x01"
    parser = RDBParser(get_rdb_reader(body=body))
    assert parser.selectdb == 1


def test_simple_string_kv():
    body = b"\x00" + b"\x03key" + b"\x05value"
    parser = RDBParser(get_rdb_reader(body=body))
    val = parser.db[b"key"]
    assert val.value == b"value"
    assert val.encoding == RedisEncoding.STRING
    assert val.expiry is None


def test_kv_with_expiry_fd():
    body = b"\xfd" + (123).to_bytes(4, "little") + b"\x00" + b"\x01k" + b"\x05value"
    parser = RDBParser(get_rdb_reader(body=body))
    val = parser.db[b"k"]
    assert val.expiry == 123000
    assert val.value == b"value"


def test_kv_with_expiry_fc():
    body = b"\xfc" + (456789).to_bytes(8, "little") + b"\x00" + b"\x01a" + b"\x01b"
    parser = RDBParser(get_rdb_reader(body=body))
    val = parser.db[b"a"]
    assert val.expiry == 456789
    assert val.value == b"b"


def test_checksum_stored():
    parser = RDBParser(get_rdb_reader(checksum=b"\x01\x02\x03\x04\x05\x06\x07\x08"))
    assert parser.checksum == b"\x01\x02\x03\x04\x05\x06\x07\x08"

