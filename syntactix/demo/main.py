from syntactix.demo.demo_lexer import ArithmeticLexer
from syntactix.lexical.lexer import make_lexer


def main() -> None:
    """Entrypoint."""
    code = (
        "2 + 3 - 4 \n"
        "   * (1 + 4) \n"
        "   / 5.3"
    )
    lexer = make_lexer(ArithmeticLexer, code)
    tokens = lexer.scan()
    print(tokens)


if __name__ == "__main__":
    main()
