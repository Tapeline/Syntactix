from abc import abstractmethod
from collections.abc import Sequence
from typing import Any, Never

from syntactix.lexical.token import TokenLike, TokenPos
from syntactix.parser.exceptions import (
    ParserError,
    ParserInvariantError,
    ParserRequireFailedError, ParserUnexpectedTokenError,
)


class ParserBase[  # noqa: WPS230, WPS214
    Token_T: TokenLike[Any, Any], Token_Typ_T, Node_T
]:
    """LL Parser base."""

    def __init__(self, tokens: Sequence[Token_T]) -> None:
        """Init parser."""
        self.tokens = tokens
        self.i = 0

    def error(self, error_class: type[ParserError], **kwargs: Any) -> Never:
        """Raise an error at current pos."""
        raise error_class(pos=self.pos, **kwargs)

    def inc_pos(self, delta: int = 1) -> None:
        """Increment position."""
        self.i += delta

    @property
    def is_at_end(self) -> bool:
        """Is at end."""
        return self.i >= len(self.tokens)

    @property
    def not_at_end(self) -> bool:
        """Check if some tokens left."""
        return not self.is_at_end

    @property
    def pos(self) -> TokenPos:
        """Get current caret position."""
        if tok := self.peek:
            return tok.pos
        return tok[-1].pos

    def lookahead(self, delta: int = 0) -> Token_T | None:
        """Look n tokens ahead from peek."""
        if self.i + delta >= len(self.tokens):
            return None
        return self.tokens[self.i + delta]

    @property
    def peek(self) -> Token_T | None:
        """Look at current token without consuming it."""
        return self.lookahead()

    @property
    def prev(self) -> Token_T | None:
        """Look at previous char."""
        return self.lookahead(-1)

    @property
    def next(self) -> Token_T | None:
        """Look at next token without consuming it."""
        return self.lookahead(1)

    @property
    def peek_rq(self) -> Token_T | Never:
        if (token := self.peek) is None:
            raise ParserInvariantError
        return token

    @property
    def prev_rq(self) -> Token_T | Never:
        if (token := self.prev) is None:
            raise ParserInvariantError
        return token

    @property
    def next_rq(self) -> Token_T | Never:
        if (token := self.next) is None:
            raise ParserInvariantError
        return token

    def consume(self) -> Token_T | None:
        if self.is_at_end:
            return None
        self.inc_pos(1)
        return self.prev_rq

    def match(self, *types: Token_Typ_T | str) -> Token_T | None:
        if self.is_at_end:
            return None
        for t_type in types:
            if isinstance(t_type, str):
                if self.peek_rq.lexeme == t_type:
                    return self.consume()
            else:
                if self.peek_rq.type == t_type:
                    return self.consume()
        return None

    def pattern_ahead(
            self, *pattern: Token_Typ_T | str | tuple[Token_Typ_T | str, ...]
    ) -> bool:
        if self.i + len(pattern) >= len(self.tokens):
            return False
        return all(
            self.tokens[self.i + i].lexeme == pattern_item
            if isinstance(pattern_item, str)
            else (
                any(
                    self.tokens[self.i + i].lexeme == subitem
                    if isinstance(subitem, str)
                    else self.tokens[self.i + i].type == subitem
                    for subitem in pattern_item
                )
                if isinstance(pattern_item, tuple)
                else self.tokens[self.i + i].type == pattern_item
            )
            for i, pattern_item in enumerate(pattern)
        )

    def match_pattern(
            self, *pattern: Token_Typ_T | str | tuple[Token_Typ_T | str, ...]
    ) -> Sequence[Token_T] | None:
        if not self.pattern_ahead(*pattern):
            return None
        tokens = self.tokens[self.i:self.i+len(pattern)]
        self.inc_pos(len(pattern))
        return tokens

    def require(self, *types: Token_Typ_T | str) -> Token_T | Never:
        if (token := self.match(*types)) is None:
            self.error(ParserRequireFailedError, tokens=types)
        return token

    @abstractmethod
    def parse(self) -> Node_T:
        """Parse."""

    def unexpected(self, token: Token_T) -> Never:
        """Mark token as unexpected and raise."""
        self.error(ParserUnexpectedTokenError, token=token)
