from values import *
from context import Context
from symbols import *
from strings import *
from tokens import *
from list import *
import math
import os

class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anon>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context
    
    def check_args(self, arg_names, args):
        res = RTResult()

        if len(args) > len(arg_names):
            return res.fail(RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed into {self}",
                self.context
            ))
        
        if len(args) < len(arg_names):
            return res.fail(RTError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed into {self}",
                self.context
            ))

        return res.success(None)
    
    def populate_args(self, arg_names, args, exec_context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_context)
            exec_context.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_context):
        result = RTResult()

        result.register(self.check_args(arg_names, args))
        if result.should_return(): return result
        self.populate_args(arg_names, args, exec_context)
        return result.success(None)

class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.auto_return = auto_return

    def execute(self, args):
        from interpreter import Interpreter
        result = RTResult()
        the_interpreter = Interpreter()
        exec_context = self.generate_new_context()
        
        result.register(self.check_and_populate_args(self.arg_names, args, exec_context))
        if result.should_return(): return result

        value = result.register(the_interpreter.visit(self.body_node, exec_context))
        if result.should_return() and result.func_return_value == None: return result
        
        return_val = (value if self.auto_return else None) or result.func_return_value or Number.null
        return result.success(return_val)
    
    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.auto_return)
        copy.set_context(self.context)
        copy.set_position(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f"<function> {self.name}>"

class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        result = RTResult()
        exec_context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        result.register(self.check_and_populate_args(method.arg_names, args, exec_context))
        if result.should_return(): return result

        return_value = result.register(method(exec_context))
        if result.should_return(): return result
        return result.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')
    
    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_position(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f"<built-in function {self.name}>"
    
    def execute_print(self, exec_context):
        print(str(exec_context.symbol_table.get('value')))
        return RTResult().success(Number.null)
    execute_print.arg_names = ["value"]


    def execute_input(self, exec_context):
        text = input()
        return RTResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, exec_context):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")
        return RTResult().success(Number(number))
    execute_input_int.arg_names = []

    def execute_clear(self, exec_context):
        os.system('cls' if os.name == 'nt' else 'clear')
        return RTResult().success(Number.null)
    execute_clear.arg_names = []

    def execute_is_number(self, exec_context):
        is_number = isinstance(exec_context.symbol_table.get("value"), Number)
        return RTResult().success(Number.true if is_number else Number.false)
    execute_is_number.arg_names = ['value']

    def execute_is_string(self, exec_context):
        is_string = isinstance(exec_context.symbol_table.get("value"), String)
        return RTResult().success(Number.true if is_string else Number.false)
    execute_is_string.arg_names = ['value']

    def execute_is_list(self, exec_context):
        is_list = isinstance(exec_context.symbol_table.get("value"), List)
        return RTResult().success(Number.true if is_list else Number.false)
    execute_is_list.arg_names = ['value']

    def execute_abs(self, exec_context):
        value  = exec_context.symbol_table.get("value")
        if not isinstance(value, Number):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a number",
                exec_context
            ))
        return RTResult().success(Number(abs(value.value)))
    execute_abs.arg_names = ["value"]

    def execute_sqrt(self, exec_context):
        value  = exec_context.symbol_table.get("value")
        if not isinstance(value, Number):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a number",
                exec_context
            ))
        return RTResult().success(Number(math.sqrt(value.value)))
    execute_sqrt.arg_names = ["value"]

    def execute_sin(self, exec_context):
        value  = exec_context.symbol_table.get("value")
        if not isinstance(value, Number):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a number",
                exec_context
            ))
        return RTResult().success(Number(math.sin(value.value)))
    execute_sin.arg_names = ["value"]

    def execute_cos(self, exec_context):
        value  = exec_context.symbol_table.get("value")
        if not isinstance(value, Number):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a number",
                exec_context
            ))
        return RTResult().success(Number(math.cos(value.value)))
    execute_cos.arg_names = ["value"]

    def execute_tan(self, exec_context):
        value  = exec_context.symbol_table.get("value")
        if not isinstance(value, Number):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a number",
                exec_context
            ))
        return RTResult().success(Number(math.tan(value.value)))
    execute_tan.arg_names = ["value"]

    def execute_to_upper(self, exec_context):
        value  = exec_context.symbol_table.get("value")
        if not isinstance(value, String):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a string",
                exec_context
            ))
        return RTResult().success(String(value.value.upper()))
    execute_to_upper.arg_names = ["value"]

    def execute_to_lower(self, exec_context):
        value  = exec_context.symbol_table.get("value")
        if not isinstance(value, String):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "Argument must be a string",
                exec_context
            ))
        return RTResult().success(String(value.value.lower()))
    execute_to_lower.arg_names = ["value"]

    def execute_contains(self, exec_context):
        value  = exec_context.symbol_table.get("value")
        item = exec_context.symbol_table.get("item")
        if not isinstance(value, List):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a list",
                exec_context
            ))
        contains_item = any(element.value == item.value for element in value.elements)
        return RTResult().success(Number.true if contains_item else Number.false)
    execute_contains.arg_names = ["value", "item"]

    def execute_index_of(self, exec_context):
        value  = exec_context.symbol_table.get("value")
        item = exec_context.symbol_table.get("item")
        if not isinstance(value, List):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a list",
                exec_context
            ))
        try:
            index = next(i for i, element in enumerate(value.elements) if element.value == item.value)
        except StopIteration:
            index = -1

        return RTResult().success(Number(index))
    execute_index_of.arg_names = ["value", "item"]

    def execute_substring(self, exec_context):
        value  = exec_context.symbol_table.get("value")
        start  = exec_context.symbol_table.get("start")
        end  = exec_context.symbol_table.get("end")
        if not isinstance(value, String):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a string",
                exec_context
            ))
        if not isinstance(start, Number) or not isinstance(end, Number):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "Second and third arguments must be numbers",
                exec_context
            ))

        return RTResult().success(String(value.value[start.value:end.value]))
    execute_substring.arg_names = ["value", "start", "end"]

    def execute_is_function(self, exec_context):
        is_function = isinstance(exec_context.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Number.true if is_function else Number.false)
    execute_is_function.arg_names = ['value']

    def execute_append(self, exec_context):
        list_ = exec_context.symbol_table.get("list")
        value = exec_context.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a list.",
                exec_context
            ))
        
        list_.elements.append(value)
        return RTResult().success(Number.null)
    execute_append.arg_names = ['list', 'value']

    def execute_remove(self, exec_context):
        list_ = exec_context.symbol_table.get("list")
        index = exec_context.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a list.",
                exec_context
            ))
        if not isinstance(index, Number):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be a number.",
                exec_context
            ))
        
        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                'Index is out of bounds.'
            ))
        return RTResult().success(element)
    execute_remove.arg_names = ['list', 'index']
        

    def execute_extend(self, exec_context):
        listA = exec_context.symbol_table.get("listA")
        listB = exec_context.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "First argument must be a list.",
                exec_context
            ))
        if not isinstance(listB, List):
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end,
                "Second argument must be a list.",
                exec_context
            ))
        listA.elements.extend(listB.elements)
        return RTResult().success(Number.null)
    execute_extend.arg_names = ['listA', 'listB']

    def execute_length(self, exec_context):
        list_ = exec_context.symbol_table.get("list")

        if not isinstance(list_, List):
            return RTResult().fail(RTError(
            self.pos_start, self.pos_end,
            "Argument must be list",
            exec_context
        ))

        return RTResult().success(Number(len(list_.elements)))
    execute_length.arg_names = ["list"]

    def execute_run(self, exec_context):
        from runner import run
        fn = exec_context.symbol_table.get("fn")

        if not isinstance(fn, String):
            return RTResult().fail(
                RTError(
                    self.pos_start, self.pos_end, "Argument must be a string", exec_context
                )
            )
        
        fn = fn.value

        if not fn.endswith(".el"):
            return RTResult().fail(
                RTError(
                    self.pos_start, self.pos_end, f"File \"{fn}\" must have a .el extension", exec_context
                )
            )

        try:
            with open(fn, "r") as f:
                script = f.read()
        except Exception as e:
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end, f"Failed to load script \"{fn}\"\n" + str(e),
                exec_context
            ))
        _, error = run(fn, script)

        if error:
            return RTResult().fail(RTError(
                self.pos_start, self.pos_end, f"Failed to finish executing script \"{fn}\"\n" + error.as_string(), exec_context
            ))
        
        return RTResult().success(Number.null)
    execute_run.arg_names = ['fn']

# Registering built-in functions
BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.remove = BuiltInFunction("remove")
BuiltInFunction.extend = BuiltInFunction("extend")
BuiltInFunction.length = BuiltInFunction("length")
BuiltInFunction.run = BuiltInFunction("run")
BuiltInFunction.abs = BuiltInFunction("abs")
BuiltInFunction.sqrt = BuiltInFunction("sqrt")
BuiltInFunction.sin = BuiltInFunction("sin")
BuiltInFunction.cos = BuiltInFunction("cos")
BuiltInFunction.tan = BuiltInFunction("tan")
BuiltInFunction.to_lower = BuiltInFunction("to_lower")
BuiltInFunction.to_upper = BuiltInFunction("to_upper")
BuiltInFunction.contains = BuiltInFunction("contains")
BuiltInFunction.substring = BuiltInFunction("substring")
BuiltInFunction.index_of = BuiltInFunction("index_of")



