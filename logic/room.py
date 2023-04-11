
class Room:
    def __init__(self):
        self.functions = dict()

    def add_functions(self, function_name, function):
        self.functions[function_name] = function
