from position import Position
from tokens import *
from errors import *

class Lexer:
    def __init__(self, f_name, text):
        self.f_name = f_name
        self.text = text
        self.pos = Position(-1, 0, -1, f_name, text)
        self.current_char = None
        self.next()

    def form_number(self):
        num = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1: break
                dot_count += 1
            num += self.current_char
            self.next()
        if dot_count == 0:
            return Token(TT_INT, int(num), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num), pos_start, self.pos)
        
    def form_identifier(self):
        id = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTER_DIGITS + "_":
            id += self.current_char
            self.next()

        token_type = TT_KEYWORD if id in KEYWORDS else TT_IDENTIFIER
        return Token(token_type, id, pos_start, self.pos)
    

    def form_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_cc = False
        self.next()

        escape_chars = {
            "n": "\n",
            "t": "\t"
        }

        while self.current_char != None and (self.current_char != '"' or escape_cc):
            if escape_cc:
                string += escape_chars.get(self.current_char, self.current_char)
                escape_cc = False
            else:
                if self.current_char == '\\':
                    escape_cc = True
                else:
                    string += self.current_char
                    escape_cc = False
            self.next()
        #fix bug where "hello is read as string and string comparisons

        self.next()
        return Token(TT_STRING, string, pos_start, self.pos)

    def make_neq(self):
        pos_start = self.pos.copy()
        self.next()

        if self.current_char == "=":
            self.next()
            return Token(TT_NE, pos_start = pos_start, pos_end = self.pos), None
        
        self.next()
        return None, ExpectedCharError(
            pos_start, self.pos, "'=' expected after '!'"
        )
    
    def make_eq(self):
        token_type = TT_EQ
        pos_start = self.pos.copy()
        self.next()

        if self.current_char == '=':
            self.next()
            token_type = TT_EE

        return Token(token_type, pos_start=pos_start, pos_end = self.pos)
    
    def make_lt(self):
        token_type = TT_LT
        pos_start = self.pos.copy()
        self.next()

        if self.current_char == '=':
            self.next()
            token_type = TT_LTE

        return Token(token_type, pos_start=pos_start, pos_end = self.pos)
    
    def make_gt(self):
        token_type = TT_GT
        pos_start = self.pos.copy()
        self.next()

        if self.current_char == '=':
            self.next()
            token_type = TT_GTE

        return Token(token_type, pos_start=pos_start, pos_end = self.pos)

    def next(self):
        self.pos.next(self.current_char) 
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def create_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.next()
            elif self.current_char == '$':
                self.skip_comment()
            elif self.current_char in DIGITS:
                tokens.append(self.form_number())
            elif self.current_char in LETTERS:
                tokens.append(self.form_identifier())
            elif self.current_char == '"':
                tokens.append(self.form_string())
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.next()
            elif self.current_char in ";\n":
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.next()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.next()
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.next()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.next()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.next()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.next()
            elif self.current_char == "[":
                tokens.append(Token(TT_LSQ, pos_start=self.pos))
                self.next()
            elif self.current_char == "]":
                tokens.append(Token(TT_RSQ, pos_start=self.pos))
                self.next()
            elif self.current_char == "^":
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.next()
            elif self.current_char == ":":
                tokens.append(Token(TT_COLON, pos_start=self.pos))
                self.next()
            elif self.current_char == ",":
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.next()
            elif self.current_char == "=":
                tokens.append(self.make_eq())
            elif self.current_char == ">":
                tokens.append(self.make_gt())
            elif self.current_char == "<":
                tokens.append(self.make_lt())
            elif self.current_char == "!":
                token,error = self.make_neq()
                if(error): return [], error
                tokens.append(token)
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.next()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
        
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None
    
    def skip_comment(self):
        self.next()

        while self.current_char != "\n":
            self.next()
        self.next()
