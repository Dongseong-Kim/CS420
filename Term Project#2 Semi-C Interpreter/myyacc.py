from mylexer import MyLexer
import yacc


start = 'source'


def p_source_declarefunc(p):
    'source : declarefunc'
    p[0] = p[1]


# functions


def p_declarefunc_list(p):
    'declarefunc : func declarefunc'
    p[0] = [p[1]] + p[2]


def p_declarefunc_single(p):
    'declarefunc : func'
    p[0] = [p[1]]


def p_func(p):
    """func : INT ID LPAREN paramlist RPAREN LBRACE stmtlist RBRACE
            | FLOAT ID LPAREN paramlist RPAREN LBRACE stmtlist RBRACE
            | INT ID LPAREN RPAREN LBRACE stmtlist RBRACE
            | FLOAT ID LPAREN RPAREN LBRACE stmtlist RBRACE"""
    if len(p) == 9:
        p[0] = ["function", p[1], p[2], ["parameter", p[4]], p[7], [p.lineno(1), p.lineno(8)]]
    else:
        p[0] = ["function", p[1], p[2], ["parameter", ["void"]], p[6], [p.lineno(1), p.lineno(7)]]


def p_paramlist_list(p):
    'paramlist : param COMMA paramlist'
    if p[1] == "void":
        p_error(p)
    else:
        p[0] = [p[1]] + p[3]


def p_paramlist_single(p):
    'paramlist : param'
    p[0] = [p[1]]


def p_param(p):
    """param : VOID
             | INT ID
             | FLOAT ID
             | INT STAR ID
             | FLOAT STAR ID"""
    if len(p) == 4:
        p[0] = ["id", p[1]+p[2], p[3]]
    elif len(p) == 3:
        p[0] = ["id", p[1], p[2]]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p_error(p)


# statements


def p_stmtlist_list(p):
    'stmtlist : stmt stmtlist'
    p[0] = [p[1]] + p[2]


def p_stmtlist_single(p):
    'stmtlist : stmt'
    p[0] = [p[1]]


def p_stmt(p):
    """stmt : return SEMICOLON
            | declarevar SEMICOLON
            | assignvar SEMICOLON
            | forloop
            | incre
            | if
            | funccall SEMICOLON"""
    p[0] = p[1]


def p_return(p):
    """return : RETURN
              | RETURN arithexp"""
    if len(p) == 2:
        p[0] = ["return", None, p.lineno(1)]
    else:
        p[0] = ["return", p[2], p.lineno(1)]


def p_forloop(p):
    'forloop : FOR LPAREN id ASSIGN arithexp SEMICOLON id cmp arithexp SEMICOLON incre RPAREN LBRACE stmtlist RBRACE'
    p[0] = ["for", ["assign", p[3], p[5]], ["condition", p[7], p[8], p[9]], p[11], p[14], [p.lineno(1), p.lineno(15)]]


def p_if(p):              # TODO: make rules for 'else if' and 'else'. make condition expression be precise
    'if : IF LPAREN arithexp cmp arithexp RPAREN LBRACE stmtlist RBRACE'
    p[0] = ["if", ["condition", p[3], p[4], p[5]], p[8], [p.lineno(1), p.lineno(9)]]


def p_funccall(p):
    """funccall : ID LPAREN arglist RPAREN
                | ID LPAREN RPAREN"""
    if len(p) == 5:
        p[0] = ["functioncall", p[1], ["argument", p[3]], p.lineno(1)]
    else:
        p[0] = ["functioncall", p[1], ["argument", []], p.lineno(1)]


def p_arglist_list(p):
    'arglist : arg COMMA arglist'
    p[0] = [p[1]] + p[3]


def p_arglist_single(p):
    'arglist : arg'
    p[0] = [p[1]]


def p_arg(p):
    """arg : arithexp
           | string"""
    p[0] = p[1]


# variables


def p_declarevar(p):
    """declarevar : INT varlist
                  | FLOAT varlist
                  | INT STAR varlist
                  | FLOAT STAR varlist"""
    if len(p) == 3:
        p[0] = ["declare", p[1], p[2], p.lineno(1)]
    else:
        p[0] = ["declare", p[1]+p[2], p[3], p.lineno(1)]


def p_varlist_list_id(p):
    'varlist : id COMMA varlist'
    p[0] = [p[1]] + p[3]


def p_varlist_single_id(p):
    'varlist : id'
    p[0] = [p[1]]

def p_assignvar(p):
    'assignvar : id ASSIGN arithexp'
    p[0] = ["assign", p[1], p[3], p.lineno(2)]


# arithmatic expressions


def p_arithexp(p):
    """arithexp : LPAREN arithexp RPAREN
                | term arithexptail
                | term"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = [p[2][0], p[1], p[2][1]]
    else:
        p[0] = p[2]


def p_arithexptail(p):
    """arithexptail : PLUS term arithexptail
                    | PLUS term
                    | MINUS term arithexptail
                    | MINUS term"""
    if len(p) == 3:
        p[0] = [p[1], p[2]]
    else:
        p[0] = [p[1], [p[3][0], p[2], p[3][1]]]


def p_term(p):
    """term : factor termtail
            | factor"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = [p[2][0], p[1], p[2][1]]



def p_termtail(p):
    """termtail : STAR factor termtail
                | STAR factor
                | DIVIDE factor termtail
                | DIVIDE factor"""
    if len(p) == 3:
        p[0] = [p[1], p[2]]
    else:
        p[0] = [p[1], [p[3][0], p[2], p[3][1]]]

def p_factor_num(p):
    """factor : NUMBER
              | PLUS NUMBER
              | MINUS NUMBER"""
    # print(p.lineno(1))
    if len(p) == 2:
        p[0] = ["number", p[1], p.lineno(1)]
    else:
        p[0] = ["number", p[1]+p[2], p.lineno(1)]


def p_factor_incre(p):
    'factor : incre'
    p[0] = p[1]


def p_incre_prefix(p):
    'incre : INCREMENT id'
    p[0] = ["incre", p[2], "prefix", p.lineno(1)]


def p_incre_postfix(p):
    'incre : id INCREMENT'
    p[0] = ["incre", p[1], "postfix", p.lineno(2)]


def p_factor_notnum(p):
    """factor : id
              | funccall"""
    p[0] = p[1]


def p_id(p):
    """id : ID
          | ID LBRACKET arithexp RBRACKET"""
    if len(p) == 2:
        p[0] = ["id", p[1], p.lineno(1)]
    else:
        p[0] = ["array", p[1], p[3], p.lineno(1)]


# etc


def p_cmp(p):
    """cmp : LGREATER
           | RGREATER
           | EQUAL
           | NOTEQUAL
           | RGREQUAL
           | LGREQUAL"""
    p[0] = p[1]


def p_string(p):
    'string : STRING'
    p[0] = ["string", p[1][1:-1]]


def p_error(p):
    print("Syntax error : line", p.lineno)
    exit()


mylexer = MyLexer()
lexer = mylexer.build()
tokens = mylexer.tokens
parser = yacc.yacc()