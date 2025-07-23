from io import BytesIO
from app.storage.rdb.parser import RDBParser
from app.storage.rdb.errors import InvalidMagicByte, InvalidVersionNumber
from app.storage.types import RedisEncoding


def get_rdb_reader(version=b"0003", body=b"", checksum=b"\x00" * 8):
    buffer = b"REDIS" + version + body + b"\xff" + checksum
    return BytesIO(buffer)


def test_valid_header_parsing():
    rdb = RDBParser().parse(get_rdb_reader())
    assert rdb.version == 3


def test_invalid_magic_byte():
    try:
        RDBParser().parse(BytesIO(b"WRONG0003\xff" + b"\x00" * 8))
        assert False, "Expected InvalidMagicByte"
    except InvalidMagicByte:
        pass


def test_invalid_version_number():
    try:
        RDBParser().parse(BytesIO(b"REDISbad!" + b"\xff" + b"\x00" * 8))
        assert False, "Expected InvalidVersionNumber"
    except InvalidVersionNumber:
        pass


def test_aux_field_parsing():
    body = b"\xfa" + b"\x01k" + b"\x01v"
    rdb = RDBParser().parse(get_rdb_reader(body=body))
    assert rdb.aux[b"k"] == b"v"


def test_select_db():
    body = b"\xfe" + b"\x01\x01"
    rdb = RDBParser().parse(get_rdb_reader(body=body))
    assert rdb.selectdb == 1


def test_simple_string_kv():
    body = b"\x00" + b"\x03key" + b"\x05value"
    rdb = RDBParser().parse(get_rdb_reader(body=body))
    val = rdb.db[b"key"]
    assert val.raw_bytes == b"value"
    assert val.encoding == RedisEncoding.STRING
    assert val.expiry is None


def test_kv_with_expiry_fd():
    body = b"\xfd" + (123).to_bytes(4, "little") + b"\x00" + b"\x01k" + b"\x05value"
    rdb = RDBParser().parse(get_rdb_reader(body=body))
    val = rdb.db[b"k"]
    assert val.expiry == 123000
    assert val.raw_bytes == b"value"


def test_kv_with_expiry_fc():
    body = b"\xfc" + (456789).to_bytes(8, "little") + b"\x00" + b"\x01a" + b"\x01b"
    rdb = RDBParser().parse(get_rdb_reader(body=body))
    val = rdb.db[b"a"]
    assert val.expiry == 456789
    assert val.raw_bytes == b"b"


def test_checksum_stored():
    rdb = RDBParser().parse(get_rdb_reader(checksum=b"\x01\x02\x03\x04\x05\x06\x07\x08"))
    assert rdb.checksum == b"\x01\x02\x03\x04\x05\x06\x07\x08"
