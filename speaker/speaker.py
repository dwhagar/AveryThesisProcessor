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
        self.sibling = False
        self.prePairs = []
        self.postPairs = []

        if not age is None:
            self.age = Age(age)
        else:
            self.age = None

        if not (self.sid == "CHI" or self.sid == "BRO" or self.sid == "SIS"):
            self.adult = True

        if self.sid == "BRO" or self.sid == "SIS":
            self.sibling = True

    def getStats(self):
        """Gets statistics about this speaker at this age for the target data."""
        wordCount = len(self.words)
        adjCount = 0
        adjCorrect = 0

        # Human-Readable Age Line
        ageLine = str(self.age.years) + ";" + str(self.age.months)

        # Get a count.
        for word in self.words:
            if word.adj:
                adjCount += 1
                if word.beforeNoun:
                    adjCorrect += 1

        # Calculate some simple stats.
        if adjCount > 0:
            score = adjCorrect / adjCount
        else:
            score = 0

        # Construct the lines for the CSV for prenominal and postnominal word lists.
        preText = []
        postText = []
        for pre in self.prePairs:
            preText.append(pre[0].word + "/" + pre[1].word)
        for post in self.postPairs:
            postText.append(post[0].word + "/" + post[1].word)

        preLine = ";".join(preText)
        postLine = ";".join(postText)

        return self.role, self.name, self.sex, round(self.age.decimal,4),\
               ageLine, wordCount, adjCount, adjCorrect, round(score,4) * 100, preLine, postLine