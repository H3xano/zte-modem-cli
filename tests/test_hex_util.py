from src.hex_util import hex_encode, hex_decode


def test_encode_ascii():
    # 'A' in UCS-2LE is 0x0041
    assert hex_encode("A") == "0041"


def test_encode_multi_char():
    # 'Hi' → 0x0048 0x0069
    assert hex_encode("Hi") == "00480069"


def test_decode_ascii():
    assert hex_decode("0041") == "A"


def test_decode_multi_char():
    assert hex_decode("00480069") == "Hi"


def test_roundtrip_ascii():
    text = "Hello World"
    assert hex_decode(hex_encode(text)) == text


def test_roundtrip_unicode():
    text = "Héllo"
    assert hex_decode(hex_encode(text)) == text


def test_encode_empty():
    assert hex_encode("") == ""


def test_decode_empty():
    assert hex_decode("") == ""
