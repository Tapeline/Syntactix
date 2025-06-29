from dataclasses import dataclass
from typing import Protocol, final


@dataclass(frozen=True, slots=True)
@final
class TokenPos:
    line: int
    char: int
    pos: int

    def __str__(self) -> str:
        return f"line {self.line}, char {self.char} (gpos {self.pos})"


class TokenLike[_Val_T, _Typ_T](Protocol):
    type: _Typ_T
    lexeme: str
    value: _Val_T
    pos: TokenPos
