import lex


reserved = {
    'if': 'IF',
    'for': 'FOR',
    'return': 'RETURN',
    'int': 'INT',
    'float': 'FLOAT',
    'void' : 'VOID'
}

tokens = [
    "ID",
    "NUMBER",
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "LBRACKET",
    "RBRACKET",
    "LGREATER",
    "RGREATER",
    "PLUS",
    "INCREMENT",
    "MINUS",
    "STAR",
    "DIVIDE",
    "SEMICOLON",
    "STRING",
    "COMMA",
    "ASSIGN",
    "EQUAL",
    "NOTEQUAL",
    "RGREQUAL",
    "LGREQUAL"
] + list(reserved.values())


class MyLexer:

    def __init__(self):
        self.reserved = reserved
        self.tokens = tokens
        self.lexer = None

    def t_ID(self, t):
        r"([a-zA-Z_][0-9a-zA-Z_]*)"
        t.type = self.reserved.get(t.value, 'ID')
        return t

    t_NUMBER = r"((0|[1-9][0-9]*)(\.[0-9]+)?)"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_LGREATER = r">"
    t_RGREATER = r"<"
    t_PLUS = r"\+"
    t_INCREMENT = r"\+\+"
    t_MINUS = r"-"
    t_DIVIDE = r"/"
    t_STAR = r"\*"
    t_SEMICOLON = r";"
    t_STRING = r"\".*\""
    t_COMMA = r","
    t_ASSIGN = r"="
    t_EQUAL = r"=="
    t_NOTEQUAL = r"!="
    t_RGREQUAL = r">="
    t_LGREQUAL = r"<="
    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        # print("Wrong input '%s'" % t.value[0])
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)
        return self.lexer
