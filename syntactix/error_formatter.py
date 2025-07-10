from syntactix.lexical.exceptions import LexerError
from syntactix.lexical.token import TokenPos
from syntactix.parser.exceptions import ParserError
from syntactix.text_normalizer import normalize_crlf


def format_error(
        source: str,
        pos: TokenPos,
        error_message: str,
        filename: str,
        error_header: str = "Error occurred"
) -> str:
    lines = normalize_crlf(source).split("\n")
    return (
        f"{error_header} (at {filename})\n"
        f"{pos.line + 1}  |  {lines[pos.line]}\n" +
        " " * (len(f"{pos.line + 1}  |  ") + pos.char - 1) + "^\n" +
        error_message
    )


def format_exception(
        exc: LexerError | ParserError,
        source: str,
        filename: str,
) -> str:
    return format_error(
        source, exc.pos, str(exc), filename, "Syntax error"
    )
