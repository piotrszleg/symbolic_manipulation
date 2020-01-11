from basic_expressions import *
from transformations import transformations
from parser import parser

if __name__ == "__main__":
    print("Input the expression:")
    expression=parser.parse(input())
    # expression=Not(Not(Not(Constant(True))))
    print("Input:")
    print(expression)
    print("Possible transformations:")
    for path in expression.simplify(transformations).values():
        print(" -> ".join(map(str, path)))