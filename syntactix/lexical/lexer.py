from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ClassVar, Never

from syntactix.lexical.exceptions import (
    LexerConsumeFailedError,
    LexerError,
    LexerRequireFailedError,
    LexerUnexpectedCharError,
)
from syntactix.lexical.token import TokenLike, TokenPos
from syntactix.sentinel import sentinel
from syntactix.text_normalizer import normalize_crlf

char = str


class LexerBase[  # noqa: WPS230, WPS214
    Token_T: TokenLike[Any, Any], Token_Typ_T
]:
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
    tokens: list[Token_T]
    """List of scanned tokens."""

    def __init__(self, src: str, token_cls: type[Token_T]) -> None:
        """Init lexer."""
        self.src = src
        if self.normalize_crlf_to_lf:
            self.src = normalize_crlf(src)
        self.i = 0
        self.line = 0
        self.line_i = 0
        self.start = 0
        self.tokens = []
        self.token_cls = token_cls

    def error(self, error_class: type[LexerError], **kwargs: Any) -> Never:
        """Raise an error at current pos."""
        raise error_class(pos=self.pos, **kwargs)

    def inc_pos(self, delta: int = 1) -> None:
        """Increment position."""
        self.i += delta
        self.line_i += delta

    def mark_next_line(self) -> None:
        """Mark next line start."""
        self.line_i = 0
        self.line += 1

    @property
    def is_at_end(self) -> bool:
        """Is at end."""
        return self.i >= len(self.src)

    @property
    def not_at_end(self) -> bool:
        """Check if some chars left."""
        return not self.is_at_end

    @property
    def pos(self) -> TokenPos:
        """Get current caret position."""
        return TokenPos(
            pos=self.i,
            char=self.line_i,
            line=self.line
        )

    @property
    def peek(self) -> char:
        """Look at current char without consuming it."""
        return self.src[self.i] if self.not_at_end else ""

    @property
    def prev(self) -> char:
        """Look at previous char."""
        return self.src[self.i - 1] if self.i > 0 else ""

    def consume(self) -> char | None:
        """Consume char or None if EOF."""
        if self.is_at_end:
            return None
        self.inc_pos(1)
        return self.src[self.i - 1]

    def consume_or_fail(self) -> char:
        """Consume character or fail if EOF."""
        ch = self.consume()
        if not ch:
            self.error(LexerConsumeFailedError, count=1)
        return ch

    def consume_many(self, count: int) -> str | None:
        """Consume multiple characters or return None if too few."""
        if self.i + count >= len(self.src):
            return None
        string = self.src[self.i:self.i + count]
        self.inc_pos(count)
        return string

    def consume_many_or_fail(self, count: int) -> str:
        """Consume multiple characters or fail if too few."""
        ch = self.consume()
        if not ch:
            self.error(LexerConsumeFailedError, count=count)
        return ch

    def string_ahead(self, string: str, offset: int = 0) -> bool:
        """Check if some string is ahead."""
        return self.src[
            min(self.i + offset, len(self.src) - 1):
        ].startswith(string)

    def char_ahead(self, ch: char, offset: int = 0) -> bool:
        """Check if some char is ahead."""
        ahead_pos = self.i + offset
        if ahead_pos >= len(self.src):
            return False
        return self.src[ahead_pos] == ch

    def match(self, strings: str | list[str]) -> str | None:
        """Try to match string in current position. No match - None."""
        if isinstance(strings, str):
            strings = [strings]
        for string in strings:
            if self.string_ahead(string):
                return self.consume_many(len(string))
        return None

    def require(self, strings: str | list[str]) -> str:
        """Require some string to be at this position or else error."""
        string = self.match(strings)
        if string is None:
            self.error(LexerRequireFailedError, strings=strings)
        return string

    def add_token(
            self,
            token_typ: Token_Typ_T,
            value: Any = sentinel
    ) -> Token_T:
        """Read lexeme, add token, shift start pos."""
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

    def scan(self) -> list[Token_T]:
        """Scan text for tokens."""
        while not self.is_at_end:
            self.scan_char()
        return self.tokens

    def unexpected(self, ch: char) -> Never:
        """Mark character as unexpected and raise."""
        self.error(LexerUnexpectedCharError, char=ch)

    def consume_while(
            self, cond: Callable[[], bool], *, not_at_end: bool
    ) -> str:
        """Consume characters while condition is true."""
        local_start = self.i
        # <= is implication operator
        while (not_at_end <= self.not_at_end) and cond():
            self.inc_pos()
        return self.src[local_start:self.i]

    def reset_start(self) -> None:
        """Reset start mark to current pos."""
        self.start = self.i

    @classmethod
    @abstractmethod
    def make_lexer(cls, src: str):  # type: ignore
        """Implement this to define token class."""

    @abstractmethod
    def scan_char(self) -> None:
        """Implement this to scan tokens."""


@dataclass
class LexerWrapper[Token_T: TokenLike[Any, Any], Token_Typ_T]:
    """Restricted interface for lexers."""

    _lexer: LexerBase[Token_T, Token_Typ_T]

    def scan(self) -> list[Token_T]:
        """Scan text for tokens."""
        return self._lexer.scan()


# I hate python generics, they're such an abomination
def make_lexer[Token_T: TokenLike[Any, Any] = Any, Token_Typ_T = Any](
        lexer_cls: type[LexerBase[Token_T, Token_Typ_T]],
        src: str
) -> LexerWrapper[Token_T, Token_Typ_T]:
    """Create lexer and return a restricted interface of it."""
    return LexerWrapper(lexer_cls.make_lexer(src))
