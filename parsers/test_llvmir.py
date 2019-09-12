from rbnf_rts.rbnf_api import codegen
from rbnf_rts.utils import ImmutableMap
from subprocess import CalledProcessError

try:
    codegen("./llvmir.rbnf", './llvmir.py', inline=False, k=1, traceback=True)
except CalledProcessError as e:
    print(e.stderr)

import operator
from rbnf_rts.rbnf_prims import link, Tokens, State, Cons, Nil, AST
from rbnf_rts.lexical import *
from rbnf_rts.rbnf_api import codegen
from rbnf_rts.token import Token
from pathlib import Path
import tempfile
import ast

with open("llvmir.rbnf-lex") as f:
    quotes = [
        each[len("quote "):] for each in f.read().splitlines()
        if each.startswith('quote ')
    ]

LEX = [
    r(float="[-+]?[0-9]+\.([eE][-+]?\d+)"),
    r(int='\d+'),
    r(globalIdent="@[-a-zA-Z$._][-a-zA-Z$._0-9]*"),
    r(localIdent="%[-a-zA-Z$._][-a-zA-Z$._0-9]*"),
    r(identifier="[-a-zA-Z$._][-a-zA-Z$._0-9]*"),
    r(str=r'"([^\\"]+|\\.)*?"'),
    # stackoverflow 12643009/regular-expression-for-floating-point-numbers
    r(whitespace="\s+"),
    r(other='.')
]

lexicals, run_lexer = lexer(
    *LEX,
    ignores=('whitespace', ),
    reserved_map=ImmutableMap.from_dict(
        {quote: "quote " + quote
         for quote in quotes}))

rev = {v: k for k, v in lexicals.items()}

with open("llvmir.py") as f:
    code = f.read()
    code = ast.parse(code, "llvmir.py")

scope = link(lexicals, code, scope=None)
#
for source in [
        "@gg = constant void bitcast (i8* 3 to i16*)", "%a = type {i8*, i1}",
    """
    define i8 @f (void){
        ret void
    }
    """
]:
    tokens = list(run_lexer("xxx", source))
    for each in tokens:
        print(rev[each.idint])

    a = scope['parse_START'](None, Tokens(tokens))  # assert a[0] == True
    print(a)
