from itertools import zip_longest, product, accumulate
from blist import sorteddict
from dataclasses import dataclass, field

@dataclass(unsafe_hash=True)
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