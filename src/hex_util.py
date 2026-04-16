def hex_encode(text):
    """Encode UTF-8 text to UCS-2LE 4-char hex codepoints (for SMS MessageBody)."""
    result = ""
    for char in text:
        encoded = char.encode("utf-16-le")
        codepoint = int.from_bytes(encoded, "little")
        result += f"{codepoint:04x}"
    return result


def hex_decode(hex_str):
    """Decode 4-char hex codepoints back to UTF-8 text (for reading SMS content)."""
    result = ""
    for i in range(len(hex_str) // 4):
        chunk = hex_str[i * 4 : (i + 1) * 4]
        result += chr(int(chunk, 16))
    return result
