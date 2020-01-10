from itertools import zip_longest
from blist import sorteddict
from dataclasses import dataclass, field

class Expression:
    def matches(self, other, variables):
        return True
    def cost(self):
        return 1
    def __lt__(self, other):
        return self.cost()-other.cost()

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
        path=[self]
        self.simplify_recursive(transformations, path, paths, 0, max_depth)
        return paths

    def visit(self, fn):
        fn(self)

    def replace_variables(self, variables):
        return self

@dataclass(frozen=True)
class Binary(Expression):
    operator:str
    left:Expression
    right:Expression

    def matches(self, other, variables):
        if not isinstance(other, self.__class__):
            return False
        left_matches=self.left.matches(other.left, variables)
        right_matches=self.right.matches(other.right, variables)
        return left_matches and right_matches

    def __repr__(self):
        return "({} {} {})".format(self.left, self.operator, self.right)

    def cost(self):
        return 1+self.left.cost()+self.right.cost()
    
    def prepend_each_path_element(self, left_path, right_path):
        result=[]
        if len(left_path)<len(right_path):
            fill=left_path[-1]
        else:
            fill=right_path[-1]
        for (left_element, right_element) in zip_longest(left_path, right_path, fillvalue=fill):
            result.append(self.__class__(left_element, right_element))
        return result

    def simplify_recursive(self, transformations, path, paths, depth, max_depth):
        left_paths=sorteddict()
        self.left.simplify_recursive(transformations, [self.left], left_paths, depth, max_depth)
        left_paths[self.left]=[self.left]
        right_paths=sorteddict()
        self.right.simplify_recursive(transformations, [self.right], right_paths, depth, max_depth)
        right_paths[self.right]=[self.right]
        for (left_transfromed, left_path) in left_paths.items():
            for (right_transformed, right_path) in right_paths.items():
                if not(left_transfromed==self.left and right_transformed==self.right):
                    key=self.__class__(left_transfromed, right_transformed)
                    paths[key]=path[:-1]+self.prepend_each_path_element(left_path, right_path)
        super().simplify_recursive(transformations, path, paths, depth, max_depth)

    def replace_variables(self, variables):
        return self.__class__(self.left.replace_variables(variables), self.right.replace_variables(variables))

class Or(Binary):
    def __init__(self, left, right):
        super().__init__("||", left, right)

class And(Binary):
    def __init__(self, left, right):
        super().__init__("&&", left, right)

@dataclass(frozen=True)
class Prefix(Expression):
    operator:str
    right:Expression

    def matches(self, other, variables):
        return isinstance(other, self.__class__) and self.right.matches(other.right, variables)

    def __repr__(self):
        return f"{self.operator}{self.right}"

    def cost(self):
        return 1+self.right.cost()

    def prepend_each_path_element(self, right_path):
        result=[]
        for right_element in right_path:
            result.append(self.__class__(right_element))
        return result

    def simplify(self, transformations, max_depth=10):
        paths=sorteddict()
        right_paths=self.right.simplify(transformations, max_depth)
        for right_path in right_paths.items():
            key=self.__class__(right_path[0])
            paths[key]=self.prepend_each_path_element(right_path[1])
        paths.update(super().simplify(transformations, max_depth))
        return paths

    def replace_variables(self, variables):
        return self.__class__(self.right.replace_variables(variables))

class Not(Prefix):
    def __init__(self, right):
        super().__init__("!", right)

@dataclass(frozen=True)
class Symbol(Expression):
    name:str

    def matches(self, other, variables):
        return isinstance(other, self.__class__) and self.name==other.name
    
    def __repr__(self):
        return self.name

    def cost(self):
        return 1

    def replace_variables(self, variables):
        return self

@dataclass(frozen=True)
class Constant(Expression):
    value:object

    def matches(self, other, variables):
        return isinstance(other, self.__class__) and self.value==other.value

    def __repr__(self):
        return repr(self.value)

    def cost(self):
        return 1

    def replace_variables(self, variables):
        return self

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

    def cost(self):
        return 1

def DeMorgan1(expression):
    return And(Not(expression.right.left), Not(expression.right.right))

def DeMorgan2(expression):
    return Or(Not(expression.right.left), Not(expression.right.right))

def DoubleNegation(expression):
    return expression.right.right

def TakeLeft(expression):
    return expression.left

def TakeRight(expression):
    return expression.right

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
    Transformation(Not(Or(Variable(1), Variable(2))), And(Not(Variable(1)), Variable(2))),
    Transformation(Not(And(Variable(1), Variable(2))), Or(Not(Variable(1)), Variable(2))),
    Transformation(And(Variable(1), Variable(1)), Variable(1)),
    Transformation(Or(Variable(1), Variable(1)), Variable(1)),
    Transformation(Not(Constant(True)), Constant(False)),
    Transformation(Not(Constant(False)), Constant(True))
]

# tested=Not(Not(Symbol("x")))
tested=Not(Not(Not(And(Constant(True), Constant(True)))))
print("Input")
print(tested)
print("Possible transformations")
for path in reversed(tested.simplify(transformations).values()):
    print("\t-> ".join(map(str, path)))