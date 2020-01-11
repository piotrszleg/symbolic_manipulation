from itertools import product
from operator import methodcaller, itemgetter
a=[{"a1" : "a->1", "a2" : "a->2"},
   {"b1" : "b->1", "b2" : "b->2"},
   {"c1" : "c->1", "c2" : "c->2"}]
for combination in product(*map(methodcaller("items"), a)):
    operands_transformed=map(itemgetter(0), combination)
    print(list(operands_transformed), end=" ")
    operands_paths=map(itemgetter(1), combination)
    print(list(operands_paths))