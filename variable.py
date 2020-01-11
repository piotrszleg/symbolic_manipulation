from dataclasses import dataclass, field
from expression import Expression

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