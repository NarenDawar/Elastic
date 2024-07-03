import string

TT_STRING = "STRING"
TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_REMAIN = "REMAIN"
TT_LPAREN = "LPAREN"
TT_KEYWORD = "KEYWORD"
TT_RPAREN = "RPAREN"
TT_EOF = "EOF"
TT_POW = "POWER"
TT_IDENTIFIER = "IDENTIFIER"
TT_EE = "EE"
TT_NE = "NE"
TT_LT = "LT"
TT_GT = "GT"
TT_LTE = "LTE"
TT_GTE = "GTE"
TT_EQ = 'EQ'
TT_COLON = "COLON"
TT_COMMA = "COMMA"
TT_LSQ = "LSQUARE"
TT_RSQ = "RSQUARE"
TT_NEWLINE = "NEWLINE"

KEYWORDS = [
    "let",
    "and",
    "or",
    "not",
    'if',
    'elif',
    'else',
    'repeat',
    'to',
    'step',
    'while',
    'then',
    'function',
    'end',
    'return',
    'continue',
    'break'
]

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTER_DIGITS = LETTERS + DIGITS

class Token:
    def __init__(self, type_, value=None, pos_start = None, pos_end = None):
        self.type = type_
        self.value = value

        if(pos_start):
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.next()
        if(pos_end):
            self.pos_end = pos_end.copy()

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
