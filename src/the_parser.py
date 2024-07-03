from tokens import *
from nodes import *
from results import ParseResult
from errors import InvalidSyntaxError

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.next()

    def next(self):
        self.token_index += 1
        self.update_current_token()
        return self.current_token
    
    def reverse(self, amount = 1):
        self.token_index -= amount
        self.update_current_token()
        return self.current_token
    
    def update_current_token(self):
        if self.token_index >= 0 and self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
    
    def parse(self):
        res = self.statements()
        if not res.error and self.current_token.type != TT_EOF:
            return res.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected an operator."
            ))
        return res
    
    def statements(self):
        result = ParseResult()
        statements = []
        pos_start = self.current_token.pos_start.copy()

        while self.current_token.type == TT_NEWLINE:
            result.register_adv()
            self.next()

        statement = result.register(self.statement())
        if result.error: return result
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_token.type == TT_NEWLINE:
                result.register_adv()
                self.next()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements: break
            statement = result.try_register(self.statement())
            if not statement:
                self.reverse(result.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return result.success(ListNode(
            statements, pos_start, self.current_token.pos_end.copy()
        ))
    
    def statement(self):
        result = ParseResult()
        pos_start = self.current_token.pos_start.copy()

        if(self.current_token.matches(TT_KEYWORD, 'return')):
            result.register_adv()
            self.next()

            expression = result.try_register(self.expression())
            if not expression:
                self.reverse(result.to_reverse_count)
            return result.success(ReturnNode(expression, pos_start, self.current_token.pos_start.copy()))

        if(self.current_token.matches(TT_KEYWORD, 'continue')):
            result.register_adv()
            self.next()
            return result.success(ContinueNode(pos_start, self.current_token.pos_start.copy()))

        if(self.current_token.matches(TT_KEYWORD, 'break')):
            result.register_adv()
            self.next()
            return result.success(BreakNode(pos_start, self.current_token.pos_start.copy()))

        expression = result.register(self.expression())
        if result.error:
            return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected an operator, identifier, '(', or '['"
            ))
        return result.success(expression)

    def for_expression(self):
        res = ParseResult()
        if not self.current_token.matches(TT_KEYWORD, 'repeat'):
            return res.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'repeat'"
            ))

        res.register_adv()
        self.next()

        if self.current_token.type != TT_IDENTIFIER:
            return res.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected identifier"
            ))

        var_name = self.current_token
        res.register_adv()
        self.next()

        if self.current_token.type != TT_EQ:
            return res.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '='"
            ))
        
        res.register_adv()
        self.next()

        start_value = res.register(self.expression())
        if res.error: return res

        if not self.current_token.matches(TT_KEYWORD, 'to'):
            return res.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'to'"
            ))
        
        res.register_adv()
        self.next()

        end_value = res.register(self.expression())
        if res.error: return res

        if self.current_token.matches(TT_KEYWORD, 'step'):
            res.register_adv()
            self.next()

            step_value = res.register(self.expression())
            if res.error: return res
        else:
            step_value = None

        if self.current_token.type != TT_COLON:
            return res.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected ':'"
        ))

        res.register_adv()
        self.next()

        if self.current_token.type == TT_NEWLINE:
            res.register_adv()
            self.next()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_token.matches(TT_KEYWORD, 'end'):
                return res.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'END'"
                ))

            res.register_adv()
            self.next()

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = res.register(self.statement())
        if res.error: return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

    def if_expression(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('if'))
        if res.error: return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))
    
    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TT_KEYWORD, case_keyword):
            return res.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '{case_keyword}'"
            ))

        res.register_adv()
        self.next()

        condition = res.register(self.expression())
        if res.error: return res

        if self.current_token.type == TT_NEWLINE:
            res.register_adv()
            self.next()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_token.matches(TT_KEYWORD, 'end'):
                res.register_adv()
                self.next()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error: return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('elif')
    
    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_token.matches(TT_KEYWORD, 'else'):
            res.register_adv()
            self.next()

            if self.current_token.type == TT_NEWLINE:
                res.register_adv()
                self.next()

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                if self.current_token.matches(TT_KEYWORD, 'end'):
                    res.register_adv()
                    self.next()
                else:
                    return res.fail(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected 'end'"
                ))
            else:
                expr = res.register(self.statement())
                if res.error: return res
                else_case = (expr, False)

        return res.success(else_case)
    
    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_token.matches(TT_KEYWORD, 'elif'):
            all_cases = res.register(self.if_expr_b())
            if res.error: return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error: return res
        
        return res.success((cases, else_case))

    def while_expression(self):
        res = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'while'):
            return res.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'while'"
            ))

        res.register_adv()
        self.next()

        condition = res.register(self.expression())
        if res.error:
            return res
        
        res.register_adv()
        self.next()

        if self.current_token.type == TT_NEWLINE:
            res.register_adv()
            self.next()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_token.matches(TT_KEYWORD, 'end'):
                return res.fail(InvalidSyntaxError(
            self.current_token.pos_start, self.current_token.pos_end,
            f"Expected 'end'"
            ))

            res.register_adv()
            self.next()

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(WhileNode(condition, body, False))
    

    def function_def(self):
        result = ParseResult()

        if(not self.current_token.matches(TT_KEYWORD, 'function')):
            return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected 'function'"
            ))
        
        result.register_adv()
        self.next()

        if(self.current_token.type == TT_IDENTIFIER):
            var_name = self.current_token
            result.register_adv()
            self.next()
            if(self.current_token.type != TT_LPAREN):
                return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected '('"
            ))
        else:
            return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"No function name provided."
            ))
        
        result.register_adv()
        self.next()
        arg_names = []

        if(self.current_token.type == TT_IDENTIFIER):
            arg_names.append(self.current_token)
            result.register_adv()
            self.next()

            while(self.current_token.type == TT_COMMA):
                result.register_adv()
                self.next()

                if(self.current_token.type != TT_IDENTIFIER):
                    return result.fail(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected identifier"
                ))

                arg_names.append(self.current_token)
                result.register_adv()
                self.next()

            if(self.current_token.type != TT_RPAREN):
                return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected ',' or ')'"
            ))
        else:
            if(self.current_token.type != TT_RPAREN):
                return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected ',' or ')'"
            ))

        result.register_adv()
        self.next()

        if self.current_token.type != TT_COLON:
            return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected ':'"
            ))
        
        result.register_adv()
        self.next()


        if self.current_token.type == TT_NEWLINE:
            result.register_adv()
            self.next()

            body = result.register(self.statements())
            if result.error: return result

            if not self.current_token.matches(TT_KEYWORD, 'end'):
                return result.fail(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    f"Expected 'end'"
                ))

            result.register_adv()
            self.next()

            return result.success(FunctionNode(
                var_name,
                arg_names,
                body,
                False
            ))
        else:
            # Inline function definition
            node_to_return = result.register(self.expression())
            if result.error: return result

            return result.success(FunctionNode(
                var_name, arg_names, node_to_return, True
            ))



    def atom(self):
        result = ParseResult()
        token = self.current_token

        if(token.type in (TT_INT, TT_FLOAT)):
            result.register_adv()
            self.next()
            return result.success(NumberNode(token))
        
        elif(token.type == TT_STRING):
            result.register_adv()
            self.next()
            return result.success(StringNode(token))
        
        elif(token.type == TT_IDENTIFIER):
            result.register_adv()
            self.next()
            return result.success(VarAccessNode(token))

        elif token.type == TT_LPAREN:
            result.register_adv()
            self.next()
            expression = result.register(self.expression())
            if result.error: return result
            if(self.current_token.type == TT_RPAREN):
                result.register_adv()
                self.next()
                return result.success(expression)
            else:
                return result.fail(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected ')'"
                ))
        elif token.type == TT_LSQ:
            list_expression = result.register(self.list_expression())
            if result.error: return result
            return result.success(list_expression)
            
        elif(token.matches(TT_KEYWORD, 'if')):
            if_expression = result.register(self.if_expression())
            if result.error: return result
            return result.success(if_expression)
        
        elif(token.matches(TT_KEYWORD, 'repeat')):
            for_expression = result.register(self.for_expression())
            if result.error: return result
            return result.success(for_expression)
        
        elif(token.matches(TT_KEYWORD, 'while')):
            while_expression = result.register(self.while_expression())
            if result.error: return result
            return result.success(while_expression)
        
        elif(token.matches(TT_KEYWORD, 'function')):
            function_def = result.register(self.function_def())
            if result.error: return result
            return result.success(function_def)

        return result.fail(InvalidSyntaxError(
            self.current_token.pos_start, self.current_token.pos_end,
            "Expected an int, float, identifier, +, -, '(', '[', or statement (if, while, for)"
        ))
    
    def power(self):
        return self.bin_op(self.call, (TT_POW, ), self.factor)
    
    def call(self):
        result = ParseResult()
        atom = result.register(self.atom())
        if result.error: return result

        if(self.current_token.type == TT_LPAREN):
            result.register_adv()
            self.next()
            arg_nodes = []

            if(self.current_token.type == TT_RPAREN):
                result.register_adv()
                self.next()
            else:
                arg_nodes.append(result.register(self.expression()))
                if(result.error): 
                    return result.fail(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected a ')', ']',  a datatype, or an identifier"
                    ))
                while(self.current_token.type == TT_COMMA):
                    result.register_adv()
                    self.next()

                    arg_nodes.append(result.register(self.expression()))
                    if(result.error): return result
                
                if(self.current_token.type != TT_RPAREN):
                    return result.fail(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected a ')' or ','"
                    ))
                
                result.register_adv()
                self.next()
            return result.success(CallNode(atom, arg_nodes))
        return result.success(atom)
    
    def factor(self):
        result = ParseResult()
        token = self.current_token

        if(token.type in (TT_PLUS, TT_MINUS)):
            result.register_adv()
            self.next()
            factor = result.register(self.factor())
            if result.error: return result
            return result.success(UnaryOpNode(token, factor))


        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_REMAIN))
    
    def list_expression(self):
        result = ParseResult()
        element_nodes = []
        pos_start = self.current_token.pos_start.copy()

        if(self.current_token.type != TT_LSQ):
            return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected a '[' "
            ))
        
        result.register_adv()
        self.next()

        if(self.current_token.type == TT_RSQ):
            result.register_adv()
            self.next()
        else:
            element_nodes.append(result.register(self.expression()))
            if result.error:
                return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected ']', '[', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"
                ))

            while self.current_token.type == TT_COMMA:
                result.register_adv()
                self.next()

                element_nodes.append(result.register(self.expression()))
                if result.error: return result

            if self.current_token.type != TT_RSQ:
                return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                f"Expected ',' or ']'"
                ))

            result.register_adv()
            self.next()

        return result.success(ListNode(
        element_nodes,
        pos_start,
        self.current_token.pos_end.copy()
        ))


    
    def arith_expression(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
    def comp_expression(self):
        result = ParseResult()

        if self.current_token.matches(TT_KEYWORD, 'not'):
            op_token = self.current_token
            result.register_adv()
            self.next()

            node = result.register(self.comp_expression())
            if result.error: return result
            return result.success(UnaryOpNode(op_token, node))
        
        node = result.register(self.bin_op(self.arith_expression, (TT_EE, TT_NE, TT_GT, TT_LT, TT_GTE, TT_LTE)))
    
        if result.error:
            return result.fail(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "Expected int, float, identifier, '+', '-','(', '[' or not"
            ))
        
        return result.success(node)

    def expression(self):
        result = ParseResult()
        if(self.current_token.matches(TT_KEYWORD, "let")):
            result.register_adv()
            self.next()

            if(self.current_token.type != TT_IDENTIFIER):
                return result.fail(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected an identifier"
                ))
            var_name = self.current_token
            result.register_adv()
            self.next()

            if(self.current_token.type != TT_EQ):
                return result.fail(InvalidSyntaxError(
                    self.current_token.pos_start, self.current_token.pos_end,
                    "Expected an '='"
                ))
            result.register_adv()
            self.next()
            expression = result.register(self.expression())
            if result.error: return result
            return result.success(VarAssignNode(var_name, expression))

        check =  result.register(self.bin_op(self.comp_expression, ((TT_KEYWORD, "and"), (TT_KEYWORD, "or"))))

        if(result.error): return result.fail(InvalidSyntaxError(
            self.current_token.pos_start, self.current_token.pos_end,
            "Expected a declaration, int, float, identifier, +, -,'(', '[', or statement (if, for, while)"
        ))

        return result.success(check)

    def bin_op(self, func_a, ops, func_b=None):
        if(func_b == None):
            func_b = func_a

        result = ParseResult()
        left = result.register(func_a())

        if result.error: return result

        while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
            op_token = self.current_token
            result.register_adv()
            self.next()
            right = result.register(func_b())
            if result.error: return result
            left = BinOpNode(left, op_token, right)

        return result.success(left)