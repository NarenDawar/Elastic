from errors import *

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.last_registered_advance_count = 0
        self.to_reverse_count = 0

    def register(self, result):
        self.last_registered_advance_count = result.advance_count
        self.advance_count += result.advance_count
        if result.error: self.error = result.error
        return result.node

    def register_adv(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def success(self, node):
        self.node = node
        return self
    
    def fail(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self
    
    def try_register(self, result):
        if result.error: 
            self.to_reverse_count = result.advance_count
            return None
        return self.register(result)

    
class RTResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_continue = False
        self.loop_break = False

    def register(self, result):
        self.error = result.error
        self.func_return_value = result.func_return_value
        self.loop_continue = result.loop_continue
        self.loop_break = result.loop_break
        return result.value
    
    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self
    
    def success_continue(self):
        self.reset()
        self.loop_continue = True
        return self
    
    def success_break(self):
        self.reset()
        self.loop_break = True
        return self
    
    def success(self, value):
        self.reset()
        self.value = value
        return self
    
    def fail(self, error):
        self.reset()
        self.error = error
        return self
    
    def should_return(self):
        return (
            self.error or 
            self.func_return_value or 
            self.loop_continue or self.loop_break
        )
