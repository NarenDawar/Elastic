class Position:
    def __init__(self, index, line, column, f_name, f_text):
        self.index = index
        self.line = line
        self.column = column
        self.f_name = f_name
        self.f_text = f_text

    def next(self, current_char=None):
        self.index += 1
        self.column += 1
    
        if(current_char == '\n'):
            self.line += 1
            self.column = 0

        return self
    
    def copy(self):
        return Position(self.index, self.line, self.column, self.f_name, self.f_text)