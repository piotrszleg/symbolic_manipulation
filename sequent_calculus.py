from basic_expressions import *
from transformation import ParsedTransformation
from itertools import starmap
 
formulas=[
("(($a&&$b), $o)->$t", "($a, $b, $o)->$t"),
("$o->($t, ($a&&$b))", "($o->($t,$a))  #  ($o->($t,$b))"),
("$o->($t, ($a||$b))", "$o->($t, $a, $b)"),
("($o, ($a||$b))->$t", "(($o, $a)->$t)  #  (($o, $b)->$t)"),
("$a, $b", "$b, $a")
]
transformations=(list(starmap(ParsedTransformation, formulas)))
