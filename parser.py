from basic_expressions import *
from lark import Lark, Transformer

class TreeToExpression(Transformer):
    
    def binary(self, value):
        (left, operator, right)=value 
        return Operator(operator, left, right)

    prefix          = lambda self, value: Operator(*value)
    return_first    = lambda self, value: value[0]
    expression      = return_first
    BINARY_OPERATOR = return_first
    PREFIX_OPERATOR = return_first
    symbol          = lambda self, value: Symbol(value[0])
    variable        = lambda self, value: Variable(value[0][0])
    true            = lambda self, _: Constant(True)
    false           = lambda self, _: Constant(False)

def make_parser(prefix_operators, binary_operators):
    parser_program=r"""
    expression: "(" expression ")"
              | ("true" | "True")   -> true
              | ("false" | "False") -> false
              | variable
              | symbol
              | prefix
              | binary
    
    prefix: PREFIX_OPERATOR expression
    binary: expression BINARY_OPERATOR expression
    symbol: NAME
    variable: "$" NAME
    NAME: /\w+/
    PREFIX_OPERATOR: /{}/
    BINARY_OPERATOR: /{}/
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS

    """.format("|".join(prefix_operators), "|".join(binary_operators))

    return Lark(parser_program, start='expression', parser="lalr", transformer=TreeToExpression())

parser=make_parser(["!"], ["&&", "\|\|", "->", "#", ","])