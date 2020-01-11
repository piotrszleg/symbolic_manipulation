from dataclasses import dataclass
from expression import Expression
from operator_expression import Operator
from variable import Variable

class Or(Operator):
    def __init__(self, *operands):
        self.operator="||"
        self.operands=operands

class And(Operator):
    def __init__(self, *operands):
        self.operator="&&"
        self.operands=operands

class Not(Operator):
    def __init__(self, operand):
        self.operator="!"
        self.operands=[operand]

@dataclass(frozen=True)
class Symbol(Expression):
    name:str

    def matches(self, other, variables):
        return isinstance(other, self.__class__) and self.name==other.name
    
    def __repr__(self):
        return self.name

@dataclass(frozen=True)
class Constant(Expression):
    value:object

    def matches(self, other, variables):
        return isinstance(other, self.__class__) and self.value==other.value

    def __repr__(self):
        return repr(self.value)