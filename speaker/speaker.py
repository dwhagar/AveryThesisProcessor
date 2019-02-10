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

    def getStats(self):
        """Gets statistics about this speaker at this age for the target data."""
        wordCount = len(self.words)
        adjCount = 0
        adjCorrect = 0

        for word in self.words:
            if word.adj:
                adjCount += 1
                if word.beforeNoun:
                    adjCorrect += 1

        if adjCount > 0:
            score = adjCorrect / adjCount
        else:
            score = 0

        return self.role, self.name, self.sex, self.age.decimal, wordCount, adjCount, adjCorrect, score