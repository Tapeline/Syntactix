from dataclasses import dataclass
from enum import Enum

from syntactix.lexical.lexer import LexerBase
from syntactix.lexical.token import TokenLike, TokenPos


class ArithmeticTokenType(Enum):
    NUMBER = "number"
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    LPAR = "("
    RPAR = ")"


@dataclass
class ArithmeticToken(TokenLike[str | float, ArithmeticTokenType]):
    type: ArithmeticTokenType
    lexeme: str
    value: str | float
    pos: TokenPos

    def __repr__(self) -> str:
        return repr(self.lexeme)


class ArithmeticLexer(LexerBase[ArithmeticToken, ArithmeticTokenType]):

    @classmethod
    def make_lexer(cls, src: str) -> "ArithmeticLexer":
        return ArithmeticLexer(src, ArithmeticToken)

    def scan_char(self) -> None:
        ch = self.consume()
        if not ch:
            self.unexpected("EOF")
        if ch in "()+-/*":
            self.add_token(ArithmeticTokenType(ch))
        elif ch.isnumeric():
            self.inc_pos(-1)
            self.scan_number()
        elif ch in " \t":
            self.reset_start()
        elif ch in "\r\n":
            self.mark_next_line()
            self.reset_start()
        else:
            self.unexpected(ch)

    def scan_number(self) -> None:
        number_str = self.consume_while(
            lambda: self.peek in "0123456789.",
            not_at_end=True
        )
        self.add_token(ArithmeticTokenType.NUMBER, float(number_str))
