from itertools import zip_longest, product, accumulate
from blist import sorteddict
from dataclasses import dataclass, field
from operator import methodcaller, itemgetter, add
from functools import reduce

class Expression:
    def matches(self, other, variables):
        return True
    def cost(self):
        return 1
    def __lt__(self, other):
        return self.cost()>other.cost()

    def possible_transformations(self, transformations):
        for transformation in transformations:
            variables={}
            if transformation.matches(self, variables):
                yield transformation.transform(self, variables)

    def simplify_recursive(self, transformations, path, paths, depth, max_depth):
        if depth>max_depth:
            return
        for transformation in self.possible_transformations(transformations):
            if not transformation in paths:
                path.append(transformation)
                paths[transformation]=path
                transformation.simplify_recursive(transformations, path.copy(), paths, depth+1, max_depth)

    def simplify(self, transformations, max_depth=10):
        paths=sorteddict()
        self.simplify_recursive(transformations, [self], paths, 0, max_depth)
        return paths

    def visit(self, fn):
        fn(self)

    def replace_variables(self, variables):
        return self

@dataclass(unsafe_hash=True, eq=False)
class Operator(Expression):
    def __init__(self, operator, *operands):
        self.operator=operator
        self.operands=operands

    def __eq__(self, other):
        if (not isinstance(other, Operator) 
            or self.operator!=other.operator 
            or len(self.operands)!=len(other.operands)):
            return False
        for (self_operand, other_operand) in zip(self.operands, other.operands):
            if self_operand!=other_operand:
                return False
        return True

    def matches(self, other, variables):
        if (not isinstance(other, Operator)
            or self.operator!=other.operator
            or len(self.operands)!=len(other.operands)):
            return False
        for (self_operand, other_operand) in zip(self.operands, other.operands):
            if not self_operand.matches(other_operand, variables):
                return False
        return True

    def __repr__(self):
        if len(self.operands)==1:
            return f"{self.operator+str(self.operands[0])}"
        else:
            return f"({self.operator.join(map(str, self.operands))})"

    def cost(self):
        return 1+reduce(add, map(methodcaller("cost"), self.operands))

    def prepend_each_path_element(self, paths):
        result=[]
        for i in range(0, max(map(len, paths), default=0)):
            operands=[]
            for path in paths:
                if i<len(path):
                    operands.append(path[i])
                else:
                    operands.append(path[-1])
            result.append(Operator(self.operator, *operands))
        return result

    def simplify_operands(self, depth, max_depth):
        operands_simplifications=[]
        for operand in self.operands:
            operand_paths={}
            operand_paths[operand]=[operand]
            operand.simplify_recursive(transformations, [], operand_paths, depth, max_depth)
            operands_simplifications.append(operand_paths)
        return operands_simplifications

    def simplify_recursive(self, transformations, path, paths, depth, max_depth):
        operands_simplifications=self.simplify_operands(depth, max_depth)
        # the default map iterator yields keys, but we need key value pairs
        operands_simplifications_items=map(methodcaller("items"), operands_simplifications)
        for combination in product(*operands_simplifications_items):
            # combination is an array of tuples
            # so here it is splitted into two arrays of first and second tuple elements
            operands_transformed=list(map(itemgetter(0), combination))
            operands_paths=list(map(itemgetter(1), combination))
            # operands simplifications are written as if each operand was the root
            # so key and each path element needs to be wrapped in the Operator instance
            key=Operator(self.operator, *operands_transformed)
            # this avoids infinite recursion
            if key!=self:
                paths[key]=path[-1:]+self.prepend_each_path_element(operands_paths)
                key.simplify_recursive(transformations, paths[key].copy(), paths, depth+1, max_depth)
        super().simplify_recursive(transformations, path.copy(), paths, depth, max_depth)

    def replace_variables(self, variables):
        return Operator(self.operator, 
                              *map(methodcaller("replace_variables", variables), self.operands))

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

@dataclass(frozen=True)
class Variable(Expression):
    identifier:object
    signature:Expression = field(default_factory=Expression)

    def matches(self, other, variables):
        if(self.signature.matches(other, variables)):
            if self.identifier in variables and not variables[self.identifier]==other:
                return False
            variables[self.identifier]=other
            return True
        else:
            return False

    def replace_variables(self, variables):
        if self.identifier in variables:
            return variables[self.identifier]
        else:
            return self

    def __repr__(self):
        return "$"+repr(self.identifier)

class Transformation:
    def __init__(self, input, output):
        self.input=input
        self.output=output
    
    def matches(self, expression, variables):
        return self.input.matches(expression, variables)

    def transform(self, expression, variables):
        return self.output.replace_variables(variables)

transformations=[
    Transformation(Not(Not(Variable(1))), Variable(1)),
    Transformation(Not(Or(Variable(1), Variable(2))), And(Not(Variable(1)), Not(Variable(2)))),
    Transformation(Not(And(Variable(1), Variable(2))), Or(Not(Variable(1)), Not(Variable(2)))),
    Transformation(And(Variable(1), Variable(1)), Variable(1)),
    Transformation(Or(Variable(1), Variable(1)), Variable(1)),
    Transformation(Not(Constant(True)), Constant(False)),
    Transformation(Not(Constant(False)), Constant(True))
]

if __name__ == "__main__":
    tested=Not(Not(Not(Constant(True))))
    print("Input")
    print(tested)
    print("Possible transformations")
    for path in tested.simplify(transformations).values():
        print(" -> ".join(map(str, path)))