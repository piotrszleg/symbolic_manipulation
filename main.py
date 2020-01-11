from basic_expressions import *
from transformations import transformations

if __name__ == "__main__":
    tested=Not(Not(Not(Constant(True))))
    print("Input")
    print(tested)
    print("Possible transformations")
    for path in tested.simplify(transformations).values():
        print(" -> ".join(map(str, path)))