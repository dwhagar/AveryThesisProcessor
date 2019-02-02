class Word:
    """A class to store information on an individual word."""
    def __init__(self, word = None, adj = False, beforeNoun = False):
        self.word = word
        self.adj = adj
        self.beforeNoun = beforeNoun