def normalize_crlf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")
