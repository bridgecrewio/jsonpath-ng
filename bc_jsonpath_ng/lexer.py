from __future__ import annotations

import logging
import sys

import ply.lex

from bc_jsonpath_ng.exceptions import JsonPathLexerError

logger = logging.getLogger(__name__)


class JsonPathLexer:
    """
    A Lexical analyzer for JsonPath.
    """

    def __init__(self, debug=False):
        self.debug = debug
        if self.__doc__ is None:
            raise JsonPathLexerError(
                "Docstrings have been removed! By design of PLY, jsonpath-rw requires docstrings. You must not use PYTHONOPTIMIZE=2 or python -OO."
            )

    def tokenize(self, string):
        """
        Maps a string to an iterator over tokens. In other words: [char] -> [token]
        """

        new_lexer = ply.lex.lex(module=self, debug=self.debug, errorlog=logger)
        new_lexer.latest_newline = 0
        new_lexer.string_value = None
        new_lexer.input(string)

        while True:
            t = new_lexer.token()
            if t is None:
                break
            t.col = t.lexpos - new_lexer.latest_newline
            yield t

        if new_lexer.string_value is not None:
            raise JsonPathLexerError("Unexpected EOF in string literal or identifier")

    # ============== PLY Lexer specification ==================
    #
    # This probably should be private but:
    #   - the parser requires access to `tokens` (perhaps they should be defined in a third, shared dependency)
    #   - things like `literals` might be a legitimate part of the public interface.
    #
    # Anyhow, it is pythonic to give some rope to hang oneself with :-)

    literals = ["*", ".", "[", "]", "(", ")", "$", ",", ":", "|", "&", "~"]

    reserved_words = {"where": "WHERE", "contains": "CONTAINS"}

    tokens = ["DOUBLEDOT", "DOUBLE_AND", "DOUBLE_OR", "NUMBER", "ID", "NAMED_OPERATOR", *list(reserved_words.values())]

    states = [("singlequote", "exclusive"), ("doublequote", "exclusive"), ("backquote", "exclusive")]

    # Normal lexing, rather easy
    t_DOUBLEDOT = r"\.\."  # noqa: N815
    t_DOUBLE_AND = "&&"  # noqa: N815
    t_DOUBLE_OR = r"\|\|"  # noqa: N815
    t_ignore = " \t"

    def t_ID(self, t):  # noqa: N802
        r"[a-zA-Z_@][a-zA-Z0-9_@\-]*"
        t.type = self.reserved_words.get(t.value, "ID")
        return t

    def t_NUMBER(self, t):  # noqa: N802
        r"-?\d+"
        t.value = int(t.value)
        return t

    # Single-quoted strings
    t_singlequote_ignore = ""

    def t_singlequote(self, t):
        r"'"
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.string_value = ""
        t.lexer.push_state("singlequote")

    def t_singlequote_content(self, t):
        r"[^'\\]+"
        t.lexer.string_value += t.value

    def t_singlequote_escape(self, t):
        r"\\."
        t.lexer.string_value += t.value[1]

    def t_singlequote_end(self, t):
        r"'"
        t.value = t.lexer.string_value
        t.type = "ID"
        t.lexer.string_value = None
        t.lexer.pop_state()
        return t

    def t_singlequote_error(self, t):
        raise JsonPathLexerError(
            f"Error on line {t.lexer.lineno}, col {t.lexpos - t.lexer.latest_newline} while lexing singlequoted field: Unexpected character: {t.value[0]} "
        )

    # Double-quoted strings
    t_doublequote_ignore = ""

    def t_doublequote(self, t):
        r'"'
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.string_value = ""
        t.lexer.push_state("doublequote")

    def t_doublequote_content(self, t):
        r'[^"\\]+'
        t.lexer.string_value += t.value

    def t_doublequote_escape(self, t):
        r"\\."
        t.lexer.string_value += t.value[1]

    def t_doublequote_end(self, t):
        r'"'
        t.value = t.lexer.string_value
        t.type = "ID"
        t.lexer.string_value = None
        t.lexer.pop_state()
        return t

    def t_doublequote_error(self, t):
        raise JsonPathLexerError(
            f"Error on line {t.lexer.lineno}, col {t.lexpos - t.lexer.latest_newline} while lexing doublequoted field: Unexpected character: {t.value[0]} "
        )

    # Back-quoted "magic" operators
    t_backquote_ignore = ""

    def t_backquote(self, t):
        r"`"
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.string_value = ""
        t.lexer.push_state("backquote")

    def t_backquote_escape(self, t):
        r"\\."
        t.lexer.string_value += t.value[1]

    def t_backquote_content(self, t):
        r"[^`\\]+"
        t.lexer.string_value += t.value

    def t_backquote_end(self, t):
        r"`"
        t.value = t.lexer.string_value
        t.type = "NAMED_OPERATOR"
        t.lexer.string_value = None
        t.lexer.pop_state()
        return t

    def t_backquote_error(self, t):
        raise JsonPathLexerError(
            f"Error on line {t.lexer.lineno}, col {t.lexpos - t.lexer.latest_newline} while lexing backquoted operator: Unexpected character: {t.value[0]} "
        )

    # Counting lines, handling errors
    def t_newline(self, t):
        r"\n"
        t.lexer.lineno += 1
        t.lexer.latest_newline = t.lexpos

    def t_error(self, t):
        raise JsonPathLexerError(
            f"Error on line {t.lexer.lineno}, col {t.lexpos - t.lexer.latest_newline}: Unexpected character: {t.value[0]} "
        )


if __name__ == "__main__":
    logging.basicConfig()
    lexer = JsonPathLexer(debug=True)
    for _token in lexer.tokenize(sys.stdin.read()):
        print("%-20s%s" % (_token.value, _token.type))  # noqa: T201
