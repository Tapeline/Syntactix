from dataclasses import dataclass

from syntactix.lexical.token import TokenPos


class LexerError(Exception):
    """Base lexer error."""

    pos: TokenPos

    def __init__(self, pos: TokenPos) -> None:
        """Init base."""
        self.pos = pos

    def __str__(self) -> str:
        """Text report."""
        return f"Lexer failed at {self.pos}"


@dataclass
class LexerConsumeFailedError(LexerError):
    pos: TokenPos
    count: int = 1

    def __str__(self) -> str:
        """Text report."""
        return (
            f"Tried to consume {self.count} chars, "
            f"but found too few or EOF at {self.pos}"
        )


@dataclass
class LexerRequireFailedError(LexerError):
    pos: TokenPos
    strings: list[str]

    def __str__(self) -> str:
        """Text report."""
        if len(self.strings) == 1:
            [strings] = f"'{self.strings}'"
        else:
            strings = f"one of {self.strings}"
        return (
            f"Expected {strings}, but did not found at {self.pos}"
        )


@dataclass
class LexerUnexpectedCharError(LexerError):
    pos: TokenPos
    char: str

    def __str__(self) -> str:
        """Text report."""
        return f"Unexpected char '{self.char}' at {self.pos}"
