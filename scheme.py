#! /usr/bin/python

import sys
from optparse import OptionParser
sys.path.insert(0,"../..")

tokens = (
    'QUOTE', 
    'SYMBOL', 
    'NUMBER', 
    'EQUALS', 
    'LPAREN', 'RPAREN',
    'NIL', 
    'TRUE', 'FALSE', 
    'TEXT',
    )

reserved = {
    'nil' : 'NIL',
    }

# Tokens
t_LPAREN =  r'\('
t_RPAREN =  r'\)'
t_QUOTE  =  r'\''
t_TRUE   =  r'\#t'
t_FALSE  =  r'\#f'
t_EQUALS = ur'='

def t_NUMBER(t):
    ur'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print "Line %d: Number %s is too large!" % (t.lineno,t.value)
        t.value = 0
    return t

def t_SYMBOL(t):
    r'[a-zA-Z_+=*-][a-zA-Z0-9_+*-]*'
    t.type = reserved.get(t.value,'SYMBOL')
    return t

def t_TEXT(t):
    r'\'[a-zA-Z0-9_+\*\- :,]*\''
    t.type = reserved.get(t.value,'TEXT')
    return t

def t_newline(t):
    ur'\n+'
    t.lexer.lineno += t.value.count("\n")

t_ignore  = ' \t'
    
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

## Build the lexer
import ply.lex as lex
lex.lex()

## Parsing rules

## Dictionary of names
names = {}

## Built-in Functions

def cons(lst):
    return [lst[0]] + lst[1]

def concat(lst):
    return lst[0] + lst[1]

def _list(lst):
    return lst

def car(lst):
    return lst[0][0]

def cdr(lst):
    return lst[0][1:]

def eq(lst):
    return lst[0] == lst[1]

def _and(lst):
    return not False in lst

def _or(lst):
    return True in lst

def cond(lst):
    if lst[0]:
        return lst[1]

def add(lst):
    return sum(lst)

def minus(lst):
    return -lst[0]

def _print(lst):
    print lisp_str(lst[0])

names['cons']   = cons
names['concat'] = concat
names['list']   = _list
names['car']    = car
names['cdr']    = cdr
names['eq']     = eq
names['=']      = eq
names['and']    = _and
names['or']     = _or
names['cond']   = cond
names['+']      = add
names['-']      = minus
names['print']  = _print

#  Evaluation functions

def scheme_evaluation(simb, items):
    if simb in names:
        return call(names[simb], eval_lists(items))
    else:
        return [simb] + items

def call(f, l):
    try:
        return f(eval_lists(l))  
    except TypeError:
        return f

def eval_lists(l):
    r = []
    for i in l:
        if is_list(i):
            if i:
                r.append(scheme_evaluation(i[0], i[1:]))
            else:
                r.append(i)
        else:
            r.append(i)
    return r


# Utilities functions

def is_list(l):
    return type(l) == type([]) # CHANGE

def lisp_str(l):
    if type(l) == type([]):
        if not l:
            return "()"
        r = "("
        for i in l[:-1]:
            r += lisp_str(i) + " "
        r += lisp_str(l[-1]) + ")"
        return r
    elif l is True:
        return "#t"
    elif l is False:
        return "#f"
    elif l is None:
        return 'nil'
    else:
        return str(l)

# Scheme Grammar

def p_exp_atom(p):
    'exp : atom'
    p[0] = p[1]
    print p[0]

def p_exp_quoted_list(p):
    'exp : quoted_list'
    p[0] = p[1]
    print p[0]

def p_exp_call(p):
    'exp : call'
    p[0] = p[1]
    print p[0]

def p_quoted_list(p):
    'quoted_list : QUOTE list'
    p[0] = p[2]

def p_list(p):
    'list : LPAREN items RPAREN'
    p[0] = p[2]

## Items in a scheme list

def p_items(p):
    'items : item items'
    p[0] = [p[1]] + p[2]

def p_items_empty(p):
    'items : empty'
    p[0] = []

def p_empty(p):
    'empty :'
    pass

def p_item_atom(p):
    'item : atom'
    p[0] = p[1]

def p_item_list(p):
    'item : list'
    p[0] = p[1]

def p_item_list(p):
    'item : quoted_list'
    p[0] = p[1]
        
def p_item_call(p):
    'item : call'
    p[0] = p[1]

def p_item_empty(p):
    'item : empty'
    p[0] = p[1]

# Atoms in scheme

def p_atom_symbol(p):
    'atom : SYMBOL'
    p[0] = p[1]

def p_atom_boolean(p):
    'atom : boolean'
    p[0] = p[1]

def p_atom_number(p):
    'atom : NUMBER'
    p[0] = p[1]

def p_atom_text(p):
    'atom : TEXT'
    p[0] = p[1]

def p_atom_empty(p): 
    'atom :'
    pass

def p_true(p):
    'boolean : TRUE'
    p[0] = True

def p_false(p):
    'boolean : FALSE'
    p[0] = False

def p_nil(p):
    'atom : NIL'
    p[0] = None

def p_call(p):
    'call : LPAREN SYMBOL items RPAREN'
    p[0] = scheme_evaluation(p[2], p[3])   

# Error rule for syntax errors
def p_error(p):
    print "Syntax error!! ",p


import ply.yacc as yacc
yacc.yacc()

def read_prompt():
    while 1:
        try:
            s = raw_input("$ ")
        except EOFError:
            break
        if not s:
            continue
        yacc.parse(unicode(s))

# def read_from_file(filename):
#     file = open(filename)
#     lines = file.readlines()
#     file.close
#     yacc.parse(unicode(lines))

def main(argv):
    parser = OptionParser(version="%prog 0.1")

#     parser.add_option("-f", "--file",
#                       action="store", 
#                       type="string", 
#                       dest="filename",
#                       help="read input from a specific file")
    parser.add_option("-p", "--prompt",
                      action="store_true",
                      dest="prompt",
                      help="read input from a prompt")

    (options, args) = parser.parse_args()

    if options.prompt:
        read_prompt()
    else:
        parser.print_help

#     if options.prompt and options.filename:
#         parser.error("prompt or filename are mutually exclusive")
#     elif not options.prompt and not options.filename:
#         parser.error("select either prompt or filename")
#     elif options.prompt:
#         print "p"
#         read_prompt()
#     elif options.filename:
#         print "f"
#         read_from_file(option.filename)


if __name__ == "__main__":
    main(sys.argv[1:])
