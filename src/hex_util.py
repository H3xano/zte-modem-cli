def hex_encode(text):
    """Encode UTF-8 text to UCS-2BE 4-char hex codepoints (for SMS MessageBody)."""
    return text.encode("utf-16-be").hex()


def hex_decode(hex_str):
    """Decode 4-char hex codepoints back to UTF-8 text (for reading SMS content)."""
    if not hex_str:
        return ""
    return bytes.fromhex(hex_str).decode("utf-16-be")
