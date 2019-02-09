from .age import Age

class Speaker:
    """A class to store information about a speaker."""
    def __init__(self, sid = None, role = None, name = None, sex = None, age = None, language = None):
        self.words = []
        self.sid = sid
        self.role = role
        self.name = name
        self.sex = sex
        self.language = language
        self.adult = False

        if not age is None:
            self.age = Age(age)
            if self.age.decimal >= 18:
                self.adult = True
        else:
            self.age = None