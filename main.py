from basic_expressions import *
from boolean_algebra import transformations
from parser import parser

if __name__ == "__main__":
    print("Input the expression:")
    expression=parser.parse(input())
    # expression=Not(Not(Not(Constant(True))))
    print("Input:")
    print(expression)
    print("Possible transformations:")
    for path in expression.simplify(transformations, 100).values():
        print(" <=> ".join(map(str, path)))