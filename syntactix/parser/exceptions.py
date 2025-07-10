from dataclasses import dataclass

from syntactix.lexical.token import TokenPos


class ParserError(Exception):
    """Base parser error."""

    pos: TokenPos

    def __init__(self, pos: TokenPos) -> None:
        """Init base."""
        self.pos = pos

    def __str__(self) -> str:
        """Text report."""
        return f"Parser failed at {self.pos}"


@dataclass
class ParserConsumeFailedError(ParserError):
    """Raised when consumption failed."""

    pos: TokenPos
    count: int = 1

    def __str__(self) -> str:
        """Text report."""
        return (
            f"Tried to consume {self.count} chars, "
            f"but found too few or EOF at {self.pos}"
        )


@dataclass
class ParserRequireFailedError[_Token_Typ_T](ParserError):
    """Raised when require of some string failed."""

    pos: TokenPos
    tokens: list[str | _Token_Typ_T]

    def __str__(self) -> str:
        """Text report."""
        str_repr = [
            f"'{tok}'" if isinstance(tok, str) else str(tok)
            for tok in self.tokens
        ]
        if len(str_repr) == 1:
            [strings] = str_repr
        else:
            strings = f"one of {str_repr}"
        return (
            f"Expected {strings}, but did not found at {self.pos}"
        )


@dataclass
class ParserUnexpectedTokenError[_Token_T](ParserError):
    """Raised when unexpected char encountered."""

    pos: TokenPos
    token: _Token_T

    def __str__(self) -> str:
        """Text report."""
        return f"Unexpected token '{self.token.lexeme}' at {self.pos}"


class ParserInvariantError(ValueError):
    """Internal error. Indicates that your parser is badly written :(."""
