class Speaker:
    """A class to store information about a speaker."""
    def __init__(self, sid = None, role = None, name = None, sex = None, age = None, language = None):
        self.words = []
        self.sid = sid
        self.role = role
        self.name = name
        self.sex = sex
        self.age = age
        self.language = language