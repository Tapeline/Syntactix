from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ClassVar

from syntactix.lexical.exceptions import (
    LexerConsumeFailedError,
    LexerError,
    LexerRequireFailedError, LexerUnexpectedCharError,
)
from syntactix.lexical.token import TokenLike, TokenPos
from syntactix.sentinel import sentinel

char = str


class LexerBase[_Token_T: TokenLike, _Token_Typ_T]:
    """Base lexer class."""

    normalize_crlf_to_lf: ClassVar[bool] = True

    src: str
    """Source code."""
    i: int
    """Current position in src."""
    line: int
    """Current line."""
    line_i: int
    """Current position from line start."""
    start: int
    """Position of start of current token."""
    tokens: list[_Token_T]
    """List of scanned tokens."""

    def __init__(self, src: str, token_cls: type[_Token_T]) -> None:
        """Init lexer."""
        self.src = src
        if self.normalize_crlf_to_lf:
            self.src = self.src.replace("\r\n", "\n").replace("\r", "\n")
        self.i = 0
        self.line = 0
        self.line_i = 0
        self.start = 0
        self.tokens = []
        self.token_cls = token_cls

    def error[**_Constructor_PS, _Class: LexerError](
            self,
            error_class: Callable[_Constructor_PS, Any],
            **kwargs: _Constructor_PS.kwargs
    ) -> None:
        raise error_class(pos=self.pos, **kwargs)

    def inc_pos(self, delta: int = 1) -> None:
        self.i += delta
        self.line_i += delta

    def mark_next_line(self) -> None:
        self.line_i = 0
        self.line += 1

    @property
    def is_at_end(self) -> bool:
        """Is at end."""
        return self.i >= len(self.src)

    @property
    def not_at_end(self):
        return not self.is_at_end

    @property
    def pos(self) -> TokenPos:
        return TokenPos(
            pos=self.i,
            char=self.line_i,
            line=self.line
        )

    @property
    def peek(self) -> char | None:
        return self.src[self.i] if self.not_at_end else None

    def consume(self) -> char | None:
        """Consume char."""
        if self.is_at_end:
            return None
        self.inc_pos(1)
        return self.src[self.i - 1]

    def consume_or_fail(self) -> char | None:
        ch = self.consume()
        if not ch:
            self.error(LexerConsumeFailedError, count=1)
        return ch

    def consume_many(self, count: int) -> str | None:
        if self.i + count >= len(self.src):
            return None
        string = self.src[self.i:self.i + count]
        self.inc_pos(count)
        return string

    def consume_many_or_fail(self, count: int) -> str:
        ch = self.consume()
        if not ch:
            self.error(LexerConsumeFailedError, count=count)
        return ch

    def string_ahead(self, string: str, offset: int = 0) -> bool:
        return self.src[
            min(self.i + offset, len(self.src) - 1):
        ].startswith(string)

    def char_ahead(self, ch: char, offset: int = 0) -> bool:
        return self.src[min(self.i + offset, len(self.src) - 1)] == ch

    def match(self, strings: str | list[str]) -> str | None:
        if isinstance(strings, str):
            strings = [strings]
        for string in strings:
            if self.string_ahead(string):
                return self.consume_many(len(string))
        return None

    def require(self, strings: str | list[str]) -> str:
        string = self.match(strings)
        if string is None:
            self.error(LexerRequireFailedError, strings=strings)
        return string

    def add_token(
            self,
            token_typ: _Token_Typ_T,
            value: Any = sentinel
    ) -> _Token_T:
        lexeme = self.src[self.start:self.i]
        value = lexeme if value is sentinel else value
        token = self.token_cls(
            type=token_typ,
            lexeme=lexeme,
            value=value,
            pos=self.pos
        )
        self.tokens.append(token)
        self.reset_start()
        return token

    def scan(self) -> list[_Token_T]:
        while not self.is_at_end:
            self.scan_char()
        return self.tokens

    def unexpected(self, ch: char) -> None:
        self.error(LexerUnexpectedCharError, char=ch)

    def consume_while(
            self, cond: Callable[[], bool], not_at_end: bool
    ) -> str:
        local_start = self.i
        # implication <= operator
        while (not_at_end <= self.not_at_end) and cond():
            self.inc_pos()
        return self.src[local_start:self.i]

    def reset_start(self):
        self.start = self.i

    @classmethod
    @abstractmethod
    def make_lexer(cls, src: str):  # type: ignore
        """Implement this to define token class."""

    @abstractmethod
    def scan_char(self) -> None:
        """Implement this to scan tokens."""


@dataclass
class LexerWrapper[_Token_T, _Token_Typ_T]:
    _lexer: LexerBase[_Token_T, _Token_Typ_T]

    def scan(self) -> list[_Token_T]:
        return self._lexer.scan()


def make_lexer[_Token_T = Any, _Token_Typ_T = Any](
        lexer_cls: type[LexerBase[_Token_T, _Token_Typ_T]],
        src: str
) -> LexerWrapper[_Token_T, _Token_Typ_T]:
    return LexerWrapper(lexer_cls.make_lexer(src))  # type: ignore
