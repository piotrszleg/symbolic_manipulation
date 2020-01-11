from basic_expressions import *
from transformation import Transformation

transformations=[
    Transformation(Not(Not(Variable(1))), Variable(1)),
    Transformation(Not(Or(Variable(1), Variable(2))), And(Not(Variable(1)), Not(Variable(2)))),
    Transformation(Not(And(Variable(1), Variable(2))), Or(Not(Variable(1)), Not(Variable(2)))),
    Transformation(And(Variable(1), Variable(1)), Variable(1)),
    Transformation(Or(Variable(1), Variable(1)), Variable(1)),
    Transformation(Not(Constant(True)), Constant(False)),
    Transformation(Not(Constant(False)), Constant(True))
]