from basic_expressions import *
from transformation import ParsedTransformation
from itertools import starmap
 
formulas=[
    ("!!$a", "$a"),
    ("!($a&&$b)", "(!$a)||(!$b)"),
    ("!($a||$b)", "(!$a)&&(!$b)"),
    ("$a&&$a", "$a"),
    ("$a||$a", "$a"),
    ("!false", "true"),
    ("!true", "false"),
    ("true||$a", "true"),
    ("$a||true", "true"),
    ("false&&$a", "false"),
    ("$a&&false", "false"),
    ("false||$a", "$a"),
    ("$a||false", "$a"),
    ("true&&$a", "$a"),
    ("$a&&true", "$a")
]
# formulas_inverted=map(reversed, formulas)

transformations=(list(starmap(ParsedTransformation, formulas))
)#                +list(starmap(ParsedTransformation, formulas_inverted)))