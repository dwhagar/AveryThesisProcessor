import string

class Word:
    """A class to store information on an individual word."""
    def __init__(self, word = None):
        self.adj = False
        self.noun = False
        self.beforeNoun = False
        self.punctuation = False

        if word is None:
            self.word = None
        elif word in string.punctuation:
            self.punctuation = True
            self.word = word
        else:
            temp = word.split("|")
            if temp[1] == "+n":
                typ = temp[0]
                word = temp[2]
            else:
                typ = temp[0]
                word = temp[1]

            if typ == "adj":
                self.adj = True
            elif typ == "n":
                self.noun = True

            if word[-2:] == "+n":
                word = word[:-2]

            self.word = word.split("&")[0]
            self.word = self.word.split("-")[0]
            self.word = self.word.split("=")[0]