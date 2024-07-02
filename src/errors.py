from strings_with_arrows import string_with_arrows

class Error:
    def __init__(self, pos_start, pos_end, err_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.err_name = err_name
        self.details = details
    
    def as_string(self):
        result = f'{self.err_name}: {self.details}'
        result += f'\nFile {self.pos_start.f_name}, line {self.pos_start.line + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.f_text, self.pos_start, self.pos_end)
        return result
    
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=""):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Expected Character', details)

class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f'{self.err_name}: {self.details}'
        result += '\n\n' + string_with_arrows(self.pos_start.f_text, self.pos_start, self.pos_end)
        return result
    
    def generate_traceback(self):
        result = ''
        position = self.pos_start
        context = self.context

        while context:
            result = f'  File {position.f_name}, line {str(position.line + 1)}, in {context.display_name}\n' + result
            position = context.parent_entry_pos
            context = context.parent

        return 'Traceback (most recent call last):\n' + result
