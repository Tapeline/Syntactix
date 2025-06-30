from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol, final


@dataclass(frozen=True, slots=True)
@final
class TokenPos:
    """Full info about position in text."""

    line: int
    char: int
    pos: int

    def __str__(self) -> str:
        """Human readable repr."""
        return f"line {self.line}, char {self.char} (gpos {self.pos})"


class TokenLike[Val_T, Typ_T](Protocol):
    """Protocol for anything that is treated as a token."""

    @abstractmethod
    def __init__(
            self,
            *,
            type: Typ_T,  # noqa: A002
            lexeme: str,
            value: Val_T,
            pos: TokenPos
    ) -> None:
        """Create token."""

    type: Typ_T
    lexeme: str
    value: Val_T
    pos: TokenPos
