class Professor:

    def __init__(self, name, email=None):
        self.name = name
        self.email = email

    def __eq__(self, value):
        if not isinstance(value, Professor):
            raise TypeError
        return self.name == value.name

    def __str__(self):
        if self.email is not None:
            return "Pr. " + self.name + " (" + self.email + ")"
        else:
            return "Pr. " + self.name