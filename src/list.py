from values import *
from number import *

class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def addition(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None
    
    def multiplication(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)
        
    def subtraction(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.remove(other.value)
                return new_list, None
            except:
                return None, RTError(
                    other.pos_start, other.pos_end, 'Index is out of bounds', self.context
                )
        else:
            return None, Value.illegal_operation(self, other)
        
    def division(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTError(
                    other.pos_start, other.pos_end, 'Index is out of bounds', self.context
                )
        else:
            return None, Value.illegal_operation(self, other)
        
    def copy(self):
        copy = List(self.elements)
        copy.set_position(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __repr__(self):
        return f'[{", ".join([str(x) for x in self.elements])}]'
    
    def __str__(self):
        return ", ".join([str(x) for x in self.elements])