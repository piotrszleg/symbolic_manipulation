from parser import parser
import abc

class Transformation(abc.ABC):
    @abc.abstractmethod
    def matches(self, expression, variables):
        pass
    @abc.abstractmethod
    def transform(self, expression, variables):
        pass

class VariableMatchingTransformation(Transformation):
    def __init__(self, input, output):
        self.input=input
        self.output=output
    
    def matches(self, expression, variables):
        return self.input.matches(expression, variables)

    def transform(self, expression, variables):
        return self.output.replace_variables(variables)

class ParsedTransformation(VariableMatchingTransformation):
    def __init__(self, input, output):
        super().__init__(parser.parse(input), parser.parse(output))