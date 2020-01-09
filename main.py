from collections import OrderedDict
import pprint
import itertools

class Expression:
    def matches(self, other):
        return True
    def cost(self):
        return 0
    def __lt__(self, other):
        return self.cost()-other.cost()

    def possible_transformations(self, axioms):
        for axiom in axioms:
            if axiom.matches(self):
                yield axiom.transform(self)

    def simplify_recursive(self, axioms, path, paths, depth, max_depth):
        if depth>max_depth:
            return
        for transformation in self.possible_transformations(axioms):
            if not transformation in paths:
                path.append(transformation)
                paths[transformation]=path
                transformation.simplify_recursive(axioms, path.copy(), paths, depth+1, max_depth)

    def simplify(self, axioms, max_depth=10):
        paths=OrderedDict()
        path=[self]
        self.simplify_recursive(axioms, path, paths, 0, max_depth)
        return paths

class Binary(Expression):
    def __init__(self, operator, left, right):
        self.operator=operator
        self.left=left
        self.right=right

    def matches(self, other):
        return isinstance(other, self.__class__) and self.left.matches(other.left) and self.right.matches(other.right)

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
        for (left_element, right_element) in itertools.zip_longest(left_path, right_path, fillvalue=fill):
            result.append(self.__class__(left_element, right_element))
        return result

    def simplify(self, axioms, max_depth=10):
        paths={}
        left_paths=self.left.simplify(axioms, max_depth)
        left_paths[self.left]=[self.left]
        right_paths=self.right.simplify(axioms, max_depth)
        right_paths[self.right]=[self.right]
        for left_path in left_paths.items():
            for right_path in right_paths.items():
                if not(left_path[0]==self.left and right_path[0]==self.right):
                    key=self.__class__(left_path[0], right_path[0])
                    paths[key]=self.prepend_each_path_element(left_path[1], right_path[1])
        paths.update(super().simplify(axioms, max_depth))
        return paths

class Or(Binary):
    def __init__(self, left, right):
        super().__init__("||", left, right)

class And(Binary):
    def __init__(self, left, right):
        super().__init__("&&", left, right)

class Prefix(Expression):
    def __init__(self, operator, right):
        self.operator=operator
        self.right=right

    def matches(self, other):
        return isinstance(other, self.__class__) and self.right.matches(other.right)

    def __repr__(self):
        return f"{self.operator}{self.right}"

    def cost(self):
        return 1+self.right.cost()

    def prepend_each_path_element(self, right_path):
        result=[]
        for right_element in right_path:
            result.append(self.__class__(right_element))
        return result

    def simplify(self, axioms, max_depth=10):
        paths={}
        right_paths=self.right.simplify(axioms, max_depth)
        for right_path in right_paths.items():
            key=self.__class__(right_path[0])
            paths[key]=self.prepend_each_path_element(right_path[1])
        paths.update(super().simplify(axioms, max_depth))
        return paths

class Not(Prefix):
    def __init__(self, right):
        super().__init__("!", right)

class Symbol(Expression):
    def __init__(self, name):
        self.name=name

    def matches(self, other):
        return isinstance(other, self.__class__) and self.name==other.name
    
    def __repr__(self):
        return self.name

    def cost(self):
        return 1

class Constant(Expression):
    def __init__(self, value):
        self.value=value

    def matches(self, other):
        return isinstance(other, self.__class__) and self.value==other.value

    def __repr__(self):
        return repr(self.value)

    def cost(self):
        return 1

def deMorgan1(expression):
    return And(Not(expression.right.left), Not(expression.right.right))

def deMorgan2(expression):
    return Or(Not(expression.right.left), Not(expression.right.right))

def DoubleNegation(expression):
    return expression.right.right

class Axiom:
    def __init__(self, signature, transforming_function):
        self.signature=signature
        self.transforming_function=transforming_function
    
    def matches(self, expression):
        return self.signature.matches(expression)

    def transform(self, expression):
        return self.transforming_function(expression)

axioms=[
    Axiom(Not(Not(Expression())), DoubleNegation),
    Axiom(Not(Or(Expression(), Expression())), deMorgan1),
    Axiom(Not(And(Expression(), Expression())), deMorgan2)
]

# tested=Not(Not(Symbol("x")))
tested=Or(Not(Not(Constant(True))), Not(Not(Symbol("b"))))
print(tested)
for path in tested.simplify(axioms).values():
    for formula in path:
        print(f"->{formula}", end="")
    print()