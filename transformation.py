class Transformation:
    def __init__(self, input, output):
        self.input=input
        self.output=output
    
    def matches(self, expression, variables):
        return self.input.matches(expression, variables)

    def transform(self, expression, variables):
        return self.output.replace_variables(variables)