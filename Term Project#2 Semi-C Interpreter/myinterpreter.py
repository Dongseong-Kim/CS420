from myyacc import parser, lexer


class For:
    def __init__(self, condition, increment, statement, lineno):
        self.condition = condition
        self.increment = increment
        self.statement = statement
        self.lineno = lineno
        self.symbol_table = {}


class If:
    def __init__(self, statement, lineno):
        self.statement = statement
        self.lineno = lineno
        self.symbol_table = {}


class Function:
    def __init__(self, name=None, datatype=None, parameter=None, statement=None, lineno=None, func=None):
        if func is None:
            self.name = name
            self.datatype = datatype
            self.parameter = parameter
            self.statement = statement
            self.symbol_table = {}
            self.return_table = {}
            self.lineno = lineno
        else:
            self.name = func.name
            self.datatype = func.datatype
            self.parameter = func.parameter
            self.statement = func.statement
            self.symbol_table = {}
            self.return_table = func.return_table
            self.lineno = func.lineno


class CallStack:
    def __init__(self):
        self.stack = []

    def push(self, func, return_table=None):
        self.stack.append([func, 1, None, return_table])

    def pop(self):
        if not self.is_empty():
            self.stack = self.stack[:-1]

    def top(self):
        if not self.is_empty():
            return self.stack[-1]
        else:
            return None

    def is_empty(self):
        if len(self.stack) == 0:
            return True
        else:
            return False


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def make_function_table(result):
    function_table = {}

    if not isinstance(result, list):
        print("error/make_function_table.. cannot make function table: result is not a list")
        return -1

    for func in result:
        if not isinstance(func, list):
            print("error/make_function_table.. cannot make function table: func is not a list")
            return -1

        if func[0] == "function":
            if func[2] in function_table:
                print("error/make_function_table.. cannot make function table: the function is already declared")
                return -1
            else:
                function_table[func[2]] = Function(name=func[2], datatype=func[1], parameter=func[3], statement=
                func[4], lineno=func[-1])
        else:
            print("error/make_function_table.. cannot make function table: this is not a function")
            return -1

    return function_table


def interp_unit(callstack, functiontable, expr):        # return caculation result or None
    # print(expr)
    expr_type = expr[0]
    if expr_type == "number":
        if is_int(expr[1]):
            return int(expr[1])
        elif is_float(expr[1]):
            return float(expr[1])
        else:
            # print("error/interp_unit.. invalid number")
            return None
    elif expr_type == "functioncall":
        func_name = expr[1]
        if func_name not in functiontable:
            # print("error/interp_unit.. invisible function")
            return None
        func_arg = expr[2][1]
        callee = Function(func=functiontable[func_name])
        func_param = callee.parameter[1]
        return_table = None

        for block in reversed(callstack.stack):
            if block[1] == 1:
                continue
            if isinstance(block[0], Function):
                return_table = block[0].return_table
                # print(return_table)
                break
        if return_table is None:
            # print("error/interp_unit.. something wrong")
            return None

        if func_param[0] == "void":
            if len(func_arg) == 0:
                if func_name in return_table and len(return_table[func_name]) > 0:
                    value = return_table[func_name][0]
                    return_table[func_name] = return_table[func_name][1:]
                    return value
                else:
                    callstack.push(func=callee, return_table=return_table)
                    return "functioncall"
            else:
                # print("error/interp_unit.. mismatch between parameter and argument")
                return None
        else:
            # print(expr)
            if len(func_param) != len(func_arg):
                # print("error/interp_unit.. mismatch between parameter and argument")
                return None
            else:
                length = len(func_param)
                for i in range(0, length):
                    param = func_param[i]
                    arg = interp_unit(callstack, functiontable, func_arg[i])
                    if isinstance(arg, str):
                        return "functioncall"
                    elif arg is None:
                        # print("error/interp_unit.. invalid argument")
                        return None
                    # print(arg)
                    if param[1] == "int":
                        callee.symbol_table[param[2]] = ["int", int(arg), [[int(arg), callee.lineno[0]]]]
                    elif param[1] == "float":
                        callee.symbol_table[param[2]] = ["float", float(arg), [[float(arg), callee.lineno[0]]]]
                    elif param[1] == "int*":
                        callee.symbol_table[param[2]] = ["int*", arg, [[arg, callee.lineno[0]]]]
                    elif param[1] == "float*":
                        callee.symbol_table[param[2]] = ["float*", arg, [[arg, callee.lineno[0]]]]
                    else:
                        # print("error/interp_unit.. invalid parameter type")
                        return None
                if func_name in return_table and len(return_table[func_name]) > 0:
                    value = return_table[func_name][0]
                    return_table[func_name] = return_table[func_name][1:]
                    return value
                else:
                    callstack.push(func=callee, return_table=return_table)
                    return "functioncall"
    elif expr_type == "id":
        for block in reversed(callstack.stack):
            if block[1] == 1:
                continue
            symbol_table = block[0].symbol_table
            if expr[1] in symbol_table:
                if not symbol_table[expr[1]][1] is None:
                    return symbol_table[expr[1]][1]
                else:
                    # print("error/interp_unit.. not assigned")
                    return None
            if isinstance(block[0], Function):
                break
        # print("error/interp_unit.. invisible variable")
        return None
    elif expr_type == "array":
        for block in reversed(callstack.stack):
            if block[1] == 1:
                continue
            symbol_table = block[0].symbol_table
            if expr[1] in symbol_table:
                arr = symbol_table[expr[1]][1]
                index = interp_unit(callstack, functiontable, expr[2])
                if isinstance(index, str):
                    return "functioncall"
                elif (index is None) or not is_int(str(index)):
                    # print("error/interp_unit.. invalid index")
                    return None
                elif (len(arr) <= index) or (index < 0):
                    # print("error/interp_unit.. out of index range")
                    return None
                else:
                    return arr[index]
            if isinstance(block[0], Function):
                break
        # print("error/interp_unit.. invisible variable")
        return None
    elif expr_type == "incre":
        target = expr[1]
        if target[0] == "id":
            for block in reversed(callstack.stack):
                if block[1] == 1:
                    continue
                symbol_table = block[0].symbol_table
                if target[1] in symbol_table:
                    if not symbol_table[target[1]][1] is None:
                        value = symbol_table[target[1]][1]
                        symbol_table[target[1]][1] = value + 1
                        symbol_table[target[1]][2].append([value + 1, int(expr[-1])])
                        if expr[2] == "prefix":
                            value += 1
                        return value
                    else:
                        # print("error/interp_unit.. not assigned")
                        return None
                if isinstance(block[0], Function):
                    break
            # print("error/interp_unit.. invisible variable")
            return None
        elif target[0] == "array":
            for block in reversed(callstack.stack):
                if block[1] == 1:
                    continue
                symbol_table = block[0].symbol_table
                if target[1] in symbol_table:
                    arr = symbol_table[target[1]][1]
                    index = interp_unit(callstack, functiontable, target[2])
                    if isinstance(index, str):
                        return "functioncall"
                    elif (index is None) or not is_int(str(index)):
                        # print("error/interp_unit.. invalid index")
                        return None
                    elif (len(arr) <= index) or (index < 0):
                        # print("error/interp_unit.. out of index range")
                        return None
                    else:
                        value = arr[index]

                        symbol_table[target[1]][1][index] = value + 1
                        arr_log = symbol_table[target[1]][1].copy()
                        symbol_table[target[1]][2].append([arr_log, int(expr[-1])])

                        if expr[2] == "prefix":
                            value += 1
                        return value
                if isinstance(block[0], Function):
                    break
            # print("error/interp_unit.. invisible variable")
            return None
        else:
            # print("error/interp_unit.. must be id or array")
            return None
    elif expr_type == "+":
        left = interp_unit(callstack, functiontable, expr[1])
        right = interp_unit(callstack, functiontable, expr[2])
        if isinstance(left, str) or isinstance(right, str):
            return "functioncall"
        elif (left is None) or (right is None):
            return None
        else:
            return left + right
    elif expr_type == "-":
        left = interp_unit(callstack, functiontable, expr[1])
        right = interp_unit(callstack, functiontable, expr[2])
        if isinstance(left, str) or isinstance(right, str):
            return "functioncall"
        elif (left is None) or (right is None):
            return None
        else:
            return left - right
    elif expr_type == "*":
        left = interp_unit(callstack, functiontable, expr[1])
        right = interp_unit(callstack, functiontable, expr[2])
        if isinstance(left, str) or isinstance(right, str):
            return "functioncall"
        elif (left is None) or (right is None):
            return None
        else:
            return left * right
    elif expr_type == "/":
        left = interp_unit(callstack, functiontable, expr[1])
        right = interp_unit(callstack, functiontable, expr[2])
        if isinstance(left, str) or isinstance(right, str):
            return "functioncall"
        elif (left is None) or (right is None):
            return None
        elif is_int(str(left)) and is_int(str(right)):
            return int(left / right)
        else:
            return left / right
    else:
        # print("error/interp_unit.. invalid expression")
        return None


def interp_stmt(callstack, functiontable):              # return [callstack, return value]
    current = callstack.top()       # [function/if/for, line count, statement index]
    stmt = current[0].statement
    symbol_table = current[0].symbol_table
    current_stmt = None

    lineno = current[1] + current[0].lineno[0]
    # print("line " + str(lineno))
    current[1] += 1

    if current[2] is None:          # before evaluating the first statement
        if len(stmt) > 0:
            stmt_lineno = stmt[0][-1]
            if isinstance(stmt_lineno, list):
                if lineno == stmt_lineno[0]:
                    current[2] = 0
                    current_stmt = stmt[0]
                else:
                    current_stmt = None
            else:
                if lineno == stmt_lineno:
                    current[2] = 0
                    current_stmt = stmt[0]
                else:
                    current_stmt = None
    else:
        if len(stmt) - 1 == current[2]:
            current_stmt = None
        else:
            stmt_lineno = stmt[current[2]+1][-1]
            if isinstance(stmt_lineno, list):
                if stmt_lineno[0] == lineno:
                    current[2] = current[2] + 1
                    current_stmt = stmt[current[2]]
                else:
                    current_stmt = None
            else:
                if lineno == stmt_lineno:
                    current[2] = current[2] + 1
                    current_stmt = stmt[current[2]]
                else:
                    current_stmt = None
    # print(current_stmt)
    if current_stmt is None:
        return callstack
    else:
        stmt_type = current_stmt[0]
        if stmt_type == "declare":
            data_type = current_stmt[1]
            for var in current_stmt[2]:
                var_type = var[0]
                if var_type == "id":
                    if var[1] in symbol_table:
                        # print("error/interp_stmt.. already declared")
                        return None
                    else:
                        symbol_table[var[1]] = [data_type, None, [[None, int(current_stmt[3])]]]        # id -> datatype value log
                        # print(symbol_table)
                elif var_type == "array":
                    if var[1] in symbol_table:
                        # print("error/interp_stmt.. already declared")
                        return None
                    else:
                        size = interp_unit(callstack, functiontable, var[2])
                        if isinstance(size, str):
                            current[1] -= 1
                            current[2] -= 1
                            return callstack
                        if size is None:
                            # print("error/interp_stmt.. invalid array size")
                            return None
                        arr_val = []
                        arr_log = []
                        for i in range(0, size):
                            arr_val.append(None)
                            arr_log.append(None)
                        symbol_table[var[1]] = [data_type, arr_val, [[arr_log, int(current_stmt[3])]]]     # array -> datatype sized-array
                else:
                    # print("error/interp_stmt.. cannot be declared")
                    return None
            return callstack
        elif stmt_type == "assign":
            var = current_stmt[1]
            var_type = var[0]
            value = interp_unit(callstack, functiontable, current_stmt[2])
            if isinstance(value, str):
                current[1] -= 1
                current[2] -= 1
                return callstack
            if value is None:
                # print("error/interp_stmt.. invalid value")
                return None

            if var_type == "id":
                for block in reversed(callstack.stack):
                    if block[1] == 1:
                        continue
                    symbol_table = block[0].symbol_table
                    if var[1] in symbol_table:
                        data_type = symbol_table[var[1]][0]
                        if data_type == "int" and is_float(str(value)):
                            value = int(value)
                        elif data_type == "float" and is_int(str(value)):
                            value = float(value)
                        symbol_table[var[1]][1] = value
                        symbol_table[var[1]][2].append([value, int(current_stmt[-1])])
                        return callstack

                    if isinstance(block[0], Function):
                        break
                # print("error/interp_stmt.. invisible variable")
                return None
            elif var_type == "array":
                for block in reversed(callstack.stack):
                    if block[1] == 1:
                        continue
                    symbol_table = block[0].symbol_table
                    if var[1] in symbol_table:
                        arr = symbol_table[var[1]][1]
                        index = interp_unit(callstack, functiontable, var[2])
                        if isinstance(index, str):
                            current[1] -= 1
                            current[2] -= 1
                            return callstack
                        if (index is None) or not is_int(str(index)):
                            # print("error/interp_stmt.. invalid index")
                            return None
                        elif (len(arr) <= index) or (index < 0):
                            # print("error/interp_stmt.. out of index range")
                            return None
                        else:
                            data_type = symbol_table[var[1]][0]
                            if data_type == "int" and is_float(str(value)):
                                value = int(value)
                            elif data_type == "float" and is_int(str(value)):
                                value = float(value)
                            symbol_table[var[1]][1][index] = value
                            arr_log = symbol_table[var[1]][1].copy()
                            symbol_table[var[1]][2].append([arr_log, int(current_stmt[-1])])
                            return callstack
                    if isinstance(block[0], Function):
                        break
                # print("error/interp_stmt.. invisible variable")
                return None

        elif stmt_type == "incre":
            target = current_stmt[1]
            if target[0] == "id":
                if target[1] in symbol_table:
                    value = symbol_table[target[1]][1]
                    symbol_table[target[1]][1] = value + 1
                    symbol_table[target[1]][2].append([value + 1, int(current_stmt[-1])])
                    if current_stmt[2] == "prefix":
                        value += 1
                    return callstack
                else:
                    # print("error/interp_stmt.. invisible variable")
                    return None
            elif target[0] == "array":
                if target[1] in symbol_table:
                    arr = symbol_table[target[1]][1]
                    index = interp_unit(symbol_table, functiontable, target[2])
                    if isinstance(index, str):
                        current[1] -= 1
                        current[2] -= 1
                        return callstack
                    elif (index is None) or not is_int(str(index)):
                        # print("errpr/interp_stmt.. wrong index")
                        return None
                    value = arr[index]

                    symbol_table[target[1]][1][index] = value + 1
                    arr_log = []
                    for i in symbol_table[target[1]][1]:
                        arr_log.append(i)
                    symbol_table[target[1]][2].append([arr_log, int(current_stmt[-1])])

                    if current_stmt[2] == "prefix":
                        value += 1
                    return callstack
                else:
                    # print("error/interp_stmt.. invisible variable")
                    return None
            else:
                # print("error/interp_stmt.. must be id or array")
                return None
        elif stmt_type == "functioncall":
            func_name = current_stmt[1]
            if func_name == "printf":
                arg = current_stmt[2][1]
                if arg[0][0] == "string":
                    string = arg[0][1]
                    if len(arg) == 1:
                        string = string.replace("\\n", "\n")
                        print(string.strip())
                        return callstack
                    return_str = ""
                    isformat = False
                    for c in string:
                        if c == '%':
                            isformat = True
                        else:
                            if isformat:
                                value = interp_unit(callstack, functiontable, arg[1])
                                if isinstance(value, str):
                                    current[1] -= 1
                                    current[2] -= 1
                                    return callstack
                                elif value is None:
                                    # print("error/interp_stmt.. invalid argument")
                                    return None
                                if c == 'd':
                                    return_str = return_str + str(int(value))
                                elif c == 'f':
                                    return_str = return_str + str(float(value))
                                isformat = False
                            else:
                                return_str = return_str + c
                    return_str = return_str.replace("\\n", "\n")
                    print(return_str.strip())
                    return callstack
                else:
                    # print("error/interp_stmt.. the first argument of printf must be a string")
                    return None
            else:
                if func_name not in functiontable:
                    # print("error/interp_stmt.. invisible function")
                    return None
                func_arg = current_stmt[2][1]
                callee = Function(func=functiontable[func_name])
                func_param = callee.parameter[1]
                return_table = None

                for block in reversed(callstack.stack):
                    if block[1] == 1:
                        continue
                    if isinstance(block[0], Function):
                        return_table = block[0].return_table
                        # print(return_table)
                        break
                if return_table is None:
                    # print("error/interp_stmt.. something wrong")
                    return None

                if func_param[0] == "void":
                    if len(func_arg) == 0:
                        if func_name in return_table and len(return_table[func_name]) > 0:
                            value = return_table[func_name][0]
                            return_table[func_name] = return_table[func_name][1:]
                            return value
                        else:
                            current[1] -= 1
                            current[2] -= 1
                            callstack.push(func=callee, return_table=return_table)
                            return callstack
                    else:
                        # print("error/interp_stmt.. mismatch between parameter and argument")
                        return None
                else:
                    if len(func_param) != len(func_arg):
                        # print("error/interp_stmt.. mismatch between parameter and argument")
                        return None
                    else:
                        length = len(func_param)
                        for i in range(0, length):
                            param = func_param[i]
                            arg = interp_unit(callstack, functiontable, func_arg[i])
                            if isinstance(arg, str):
                                current[1] -= 1
                                current[2] -= 1
                                return callstack
                            elif arg is None:
                                # print("error/interp_stmt.. invalid argument")
                                return None
                            # print(arg)
                            if param[1] == "int":
                                callee.symbol_table[param[2]] = ["int", int(arg), [[int(arg), callee.lineno[0]]]]
                            elif param[1] == "float":
                                callee.symbol_table[param[2]] = ["float", float(arg), [[float(arg), callee.lineno[0]]]]
                            elif param[1] == "int*":
                                callee.symbol_table[param[2]] = ["int*", arg, [[arg, callee.lineno[0]]]]
                            elif param[1] == "float*":
                                callee.symbol_table[param[2]] = ["float*", arg, [[arg, callee.lineno[0]]]]
                            else:
                                # print("error/interp_stmt.. invalid parameter type")
                                return None
                        if func_name in return_table and len(return_table[func_name]) > 0:
                            value = return_table[func_name][0]
                            return_table[func_name] = return_table[func_name][1:]
                            return value
                        else:
                            current[1] -= 1
                            current[2] -= 1
                            callstack.push(func=callee, return_table=return_table)
                            return callstack

        elif stmt_type == "return":
            if current_stmt[1] is None:
                current[1] = current[0].lineno[1]
                return callstack
            else:
                return_value = interp_unit(callstack, functiontable, current_stmt[1])

                if isinstance(return_value, str):
                    current[1] -= 1
                    current[2] -= 1
                    return callstack
                elif return_value is None:
                    # print("error/interp_stmt.. wrong return value")
                    return None
                else:
                    current_func = None
                    current_block = None
                    for block in reversed(callstack.stack):
                        if not isinstance(block[0], Function):
                            continue
                        current_block = block
                        current_func = block[0]
                        break
                    if current_func is None or current_block is None:
                        # print("error/interp_stmt.. something wrong with callstack")
                        return None
                    if current_func.datatype == "int" and not is_int(str(return_value)):
                        # print("error/interp_stmt.. return type mismatch")
                        return None
                    elif current_func.datatype == "float" and not is_float(str(return_value)):
                        # print("error/interp_stmt.. return type mismatch")
                        return None

                    if current_func.name in current_block[3]:
                        current_block[3][current_func.name].append(return_value)
                    else:
                        current_block[3][current_func.name] = [return_value]
                    current_block[1] = current_block[0].lineno[1]
                    return callstack
        elif stmt_type == "for":
            initial = current_stmt[1]

            var_type = initial[1][0]
            value = interp_unit(callstack, functiontable, initial[2])
            if isinstance(value, str):
                current[1] -= 1
                return callstack
            if value is None:
                # print("error/interp_stmt.. invalid value")
                return None

            if var_type == "id":
                visible = False
                for block in reversed(callstack.stack):
                    if block[1] == 1:
                        continue
                    symbol_table = block[0].symbol_table
                    if initial[1][1] in symbol_table:
                        data_type = symbol_table[initial[1][1]][0]
                        if data_type == "int" and is_float(str(value)):
                            value = int(value)
                        elif data_type == "float" and is_int(str(value)):
                            value = float(value)
                        symbol_table[initial[1][1]][1] = value
                        symbol_table[initial[1][1]][2].append([value, int(current_stmt[-1][0])])
                        visible = True
                        break
                    else:
                        if isinstance(block[0], Function):
                            # print("error/interp_stmt.. invisible variable")
                            return None

                if not visible:
                    # print("error/interp_stmt.. invisible variable")
                    return None
#            elif var_type == "array":
#                if initial[1][1] in symbol_table:
#                    data_type = symbol_table[initial[1][1]][0]
#                    size = len(symbol_table[initial[1][1]][1])
#                    index = interp_unit(callstack, functiontable, initial[2])
#                    if index is None:
#                        print("error/interp_stmt.. invalid index")
#                        return None
#                    elif not is_int(str(index)):
#                        print("error/interp_stmt.. index must be an integer")
#                        return None
#                    elif not 0 <= index < size:
#                        print("error/interp_stmt.. out of range")
#                        return None
#                    else:
#                        if data_type == "int" and is_float(str(value)):
#                            value = int(value)
#                        elif data_type == "float" and is_int(str(value)):
#                            value = float(value)
#                        symbol_table[initial[1][1]][1][index] = value
#                        arr_log = []
#                        for i in symbol_table[initial[1][1]][1]:
#                            arr_log.append(i)
#                        symbol_table[initial[1][1]][2].append([arr_log, int(current_stmt[3])])
#                else:
#                    print("error/interp_stmt.. invisible variable")
#                    return None
            block_size = current_stmt[-1][1] - current_stmt[-1][0]
            callstack.top()[1] += block_size
            callstack.push(func=For(condition=current_stmt[2], increment=current_stmt[3], statement=current_stmt[4], lineno=current_stmt[-1]))
            return callstack

        elif stmt_type == "if":
            condition = current_stmt[1]
            condition_leftid = interp_unit(callstack, functiontable, condition[1])
            condition_cmp = condition[2]
            condition_rightid = interp_unit(callstack, functiontable, condition[3])

            if isinstance(condition_leftid, str) or isinstance(condition_rightid, str):
                current[1] -= 1
                current[2] -= 1
                return callstack
            if condition_leftid is None or condition_rightid is None:
                # print("error/interp_stmt.. invalid comparison")
                return None
            else:
                if condition_cmp == ">":
                    condition_result = condition_leftid > condition_rightid
                elif condition_cmp == "<":
                    condition_result = condition_leftid < condition_rightid
                elif condition_cmp == "==":
                    condition_result = condition_leftid == condition_rightid
                elif condition_cmp == "!=":
                    condition_result = condition_leftid != condition_rightid
                elif condition_cmp == "<=":
                    condition_result = condition_leftid <= condition_rightid
                elif condition_cmp == ">=":
                    condition_result = condition_leftid >= condition_rightid
                else:
                    # print("error/interp_stmt.. invalid cmp")
                    return None
            block_size = current_stmt[-1][1] - current_stmt[-1][0]
            callstack.top()[1] += block_size
            if condition_result:
                callstack.push(func=If(statement=current_stmt[2], lineno=current_stmt[-1]))

            return callstack
        else:
            print("Invalid statement")
            return None


def run():
    # load code file (.txt)
    file3 = open("main.txt", 'r')
    lines3 = file3.readlines()
    txt3 = " ".join(lines3)

    # syntax analysis
    result = parser.parse(txt3, lexer=lexer)

    # make function table
    function_table = make_function_table(result)
    if not isinstance(function_table, dict):
        print("Invalid function table")
        return -1

    if not ("main" in function_table):
        print("main function does not exist")
        return -1

    callstack = CallStack()
    main_function = Function(func=function_table["main"])
    callstack.push(func=main_function, return_table=dict())
    _error = False
    lineno = 0
    while not _error:
        command = input().split(" ")

        if command[0] == "test":                # debug command
            print(callstack.stack)
            continue
        elif command[0] == "next":
            if len(command) == 1:
                line_cnt = 1
            elif len(command) == 2:
                if is_int(command[1]):
                    line_cnt = int(command[1])
                else:
                    print("Incorrect command usage : try \'next [lines]\'")
                    continue
            else:
                print("Incorrect command usage : try \'next [lines]\'")
                continue
            if callstack.is_empty():
                print("End of program")
                continue
            while line_cnt > 0:
                current = callstack.top()
                lineno = current[1] + current[0].lineno[0]
                result = interp_stmt(callstack, function_table)   # result : callstack or None
                if result is None:
                    _error = True
                    break
                line_cnt = line_cnt - 1
                current_block = current[0]
                if current_block.lineno[1] - current_block.lineno[0] + 1 <= callstack.top()[1]:
                    if isinstance(current_block, For):
                        condition = current_block.condition
                        incre = current_block.increment
                        interp_unit(callstack, function_table, incre)

                        condition_left = interp_unit(callstack, function_table, condition[1])
                        condition_cmp = condition[2]
                        condition_right = interp_unit(callstack, function_table, condition[3])

                        if isinstance(condition_left, str) or isinstance(condition_right, str):
                            current[1] -= 1
                            continue
                        if condition_left is None or condition_right is None:
                            # print("error/interp_stmt.. invalid comparison")
                            _error = True
                            break
                        else:
                            if condition_cmp == ">":
                                condition_result = condition_left > condition_right
                            elif condition_cmp == "<":
                                condition_result = condition_left < condition_right
                            elif condition_cmp == "==":
                                condition_result = condition_left == condition_right
                            elif condition_cmp == "!=":
                                condition_result = condition_left != condition_right
                            elif condition_cmp == "<=":
                                condition_result = condition_left <= condition_right
                            elif condition_cmp == ">=":
                                condition_result = condition_left >= condition_right
                            else:
                                print("error/interp_stmt.. invalid cmp")
                                _error = True
                                break

                        if condition_result:
                            callstack.top()[1] = 1
                            callstack.top()[2] = None
                            current_block.symbol_table = {}
                        else:
                            callstack.pop()
                    else:
                        callstack.pop()

                if callstack.is_empty():
                    break
            if _error:
                continue
            if callstack.is_empty():
                print("End of program")
                continue

        elif command[0] == "print":
            if len(command) != 2:
                print("Invalid typing of the variable name")
                continue

            name = command[1]
            lexer.input(name)
            tok = lexer.token()

            if (tok is None) or (tok.type != "ID") or (len(tok.value) != len(name)):
                print("Invalid typing of the variable name")
                continue
            else:
                value = "None"
                if callstack.is_empty():
                    symbol_table = main_function.symbol_table
                    if name in symbol_table:
                        value = symbol_table[name][1]
                else:
                    for block in reversed(callstack.stack):
                        # print(block)
                        if block[1] == 1:
                            continue
                        symbol_table = block[0].symbol_table
                        if name in symbol_table:
                            value = symbol_table[name][1]
                            break
                        if isinstance(block[0], Function):
                            break
                if isinstance(value, str):
                    print("Invisible variable")
                elif value is None:
                    print("N/A")
                else:
                    print(value)
        elif command[0] == "trace":
            if len(command) != 2:
                print("Invalid typing of the variable name")
                continue

            name = command[1]
            lexer.input(name)
            tok = lexer.token()

            if (tok is None) or (tok.type != "ID") or (len(tok.value) != len(name)):
                print("Invalid typing of the variable name")
            else:
                history = None
                if callstack.is_empty():
                    symbol_table = main_function.symbol_table
                    if name in symbol_table:
                        history = symbol_table[name][2]
                else:
                    for block in reversed(callstack.stack):
                        if block[1] == 1:
                            continue
                        symbol_table = block[0].symbol_table
                        if name in symbol_table:
                            history = symbol_table[name][2]
                            break
                        if isinstance(block[0], Function):
                            break

                if history is None:
                    print("Invisible variable")
                else:
                    for log in history:
                        value = log[0]
                        if value is None:
                            value = "N/A"
                        print(name + " = " + str(value) + " at line " + str(log[1]))
        else:
            break

    if _error:
        print("Run-time error : line " + str(lineno))

if __name__ == "__main__":
    # run interpreter
    run()

