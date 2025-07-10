from syntactix.demo.demo_lexer import ArithmeticLexer
from syntactix.error_formatter import format_exception
from syntactix.lexical.exceptions import LexerError
from syntactix.lexical.lexer import make_lexer


def main() -> None:
    """Entrypoint."""
    code = (
        "2 + 3 - 4 \n"
        "   * (1 + 4) \n"
        "   / 5.3"
    )
    lexer = make_lexer(ArithmeticLexer, code)
    try:
        tokens = lexer.scan()
        print(tokens)
    except LexerError as e:
        print(format_exception(e, code, "<main>"))


if __name__ == "__main__":
    main()
