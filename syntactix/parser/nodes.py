from typing import Any, Protocol

from syntactix.lexical.token import TokenLike


class NodeLike[_Token_T: TokenLike[Any, Any]](Protocol):
    token: _Token_T
