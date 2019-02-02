# Data structure to hold information about what words are spoken and who speaks them.

class Word:
    """A class to store information on an individual word."""
    def __init__(self, word = None, adj = False, beforeNoun = False):
        self.word = word
        self.adj = adj
        self.beforeNoun = beforeNoun

class Age:
    """A class to store the age data from a speaker."""
    def __init__(self, ageStr = None):
        if not ageStr is None:
            self.parseAge(ageStr)

    def parseAge(self, ageStr):
        # TODO: write function to parse the date strings

class Speaker:
    """A class to store information about a speaker."""
    def __init__(self, id = None, role = None, name = None, sex = None, age = None):
        self.words = []
        self.id = id
        self.role = role
        self.name = name
        self.sex = sex
        self.age = age