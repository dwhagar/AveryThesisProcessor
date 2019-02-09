class Word:
    """A class to store information on an individual word."""
    def __init__(self, word = None):
        self.adj = False
        self.noun = False
        self.beforeNoun = False

        if word is None:
            self.word = None
        else:
            temp = word.split("|")
            typ = temp[0]
            word = temp[1]

            if typ == "adj":
                self.adj = True
            elif typ == "n":
                self.noun = True

            self.word = word.split("&")[0]