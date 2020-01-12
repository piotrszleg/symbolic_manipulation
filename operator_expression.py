from expression import Expression
from itertools import zip_longest, product, accumulate
from blist import sorteddict
from dataclasses import dataclass, field
from operator import methodcaller, itemgetter, add
from functools import reduce

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

    def simplify_operands(self, transformations, depth, max_depth):
        operands_simplifications=[]
        for operand in self.operands:
            operand_paths={}
            operand_paths[operand]=[operand]
            operand.simplify_recursive(transformations, [], operand_paths, depth, max_depth)
            operands_simplifications.append(operand_paths)
        return operands_simplifications

    def simplify_recursive(self, transformations, path, paths, depth, max_depth):
        operands_simplifications=self.simplify_operands(transformations, depth, max_depth)
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
                paths[key]=path+self.prepend_each_path_element(operands_paths)
                key.simplify_recursive(transformations, paths[key].copy(), paths, depth+1, max_depth)
        super().simplify_recursive(transformations, path.copy(), paths, depth, max_depth)

    def replace_variables(self, variables):
        return Operator(self.operator, 
                              *map(methodcaller("replace_variables", variables), self.operands))
