from .age import Age

class Speaker:
    """A class to store information about a speaker."""
    def __init__(self, sid = None, role = None, name = None, sex = None, age = None, language = None):
        self.words = []
        self.sid = sid
        self.role = role.replace("_", " ")
        self.name = name
        self.sex = sex
        self.language = language
        self.adult = False
        self.sibling = False
        self.prePairs = []
        self.postPairs = []
        self.orphans = []

        if not age is None:
            self.age = Age(age)
        else:
            self.age = None

        if self.age.decimal >= 18:
            self.adult = True

        if self.sid == "BRO" or self.sid == "SIS":
            self.sibling = True

    def getStats(self):
        """Gets statistics about this speaker at this age for the target data."""
        wordCount = len(self.words)

        # Human-Readable Age Line
        ageLine = str(self.age.years) + ";" + str(self.age.months)

        # Get a count.
        adjCount = len(self.prePairs) + len(self.postPairs)
        adjCorrect = len(self.prePairs)

        # Pre Avery's instructions, do not count the orphans.

        # Calculate some simple stats.
        if adjCount > 0:
            score = adjCorrect / adjCount
        else:
            score = 0

        return self.role, self.name, self.sex, round(self.age.decimal,4),\
               ageLine, wordCount, adjCount, adjCorrect, round(score,4) * 100

    def getAdjectives(self):
        """Gets a list of adjectives, both pre and post nomative, for this speaker."""
        resultPre = []
        resultPost = []

        # Just go through the word list and pick out the proper words.
        for item in self.prePairs:
            resultPre.append(item[0])
        for item in self.postPairs:
            resultPost.append(item[0])

        return resultPre, resultPost