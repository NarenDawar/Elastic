from lexer import Lexer
from the_parser import Parser
from interpreter import Interpreter
from context import Context
from symbols import *
from number import *
from functions import BuiltInFunction

global_symbol_table = SymbolTable()
global_symbol_table.set("Null", Number.null)
global_symbol_table.set("True", Number.true)
global_symbol_table.set("False", Number.false)
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("cls", BuiltInFunction.clear)
global_symbol_table.set("is_number", BuiltInFunction.is_number)
global_symbol_table.set("is_string", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_function", BuiltInFunction.is_function)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("remove", BuiltInFunction.remove)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("length", BuiltInFunction.length)
global_symbol_table.set("run", BuiltInFunction.run)
global_symbol_table.set("abs", BuiltInFunction.abs)
global_symbol_table.set("sqrt", BuiltInFunction.sqrt)
global_symbol_table.set("sin", BuiltInFunction.sin)
global_symbol_table.set("cos", BuiltInFunction.cos)
global_symbol_table.set("tan", BuiltInFunction.tan)
global_symbol_table.set("substring", BuiltInFunction.substring)
global_symbol_table.set("contains", BuiltInFunction.contains)
global_symbol_table.set("index_of", BuiltInFunction.index_of)
global_symbol_table.set("to_upper", BuiltInFunction.to_upper)
global_symbol_table.set("to_lower", BuiltInFunction.to_lower)






def run(f_name, text):
    lexer = Lexer(f_name, text)
    tokens, error = lexer.create_tokens()
    if error: return None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
