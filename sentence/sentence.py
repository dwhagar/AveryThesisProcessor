# This goes contrary how how the spacy docs say one should install the corpus data.
# Loading takes a long time, so we define it as a global variable so it doesn't have
# to load with each and every sentence.
import fr_core_news_lg
nlp = fr_core_news_lg.load()

class Sentence:
    """Storage of a sentence and other data from a corpus."""
    def __init__(self, speakerData, sentenceText, pos = None, post = None, pre = None, find = True):
        """
        Stores data for a single sentence.
        :param speakerData: A Speaker object denoting who uttered the sentence.
        :param sentenceText: The actual text of the sentence.
        :param pos: Pre-tagged POS data.
        :param post: Postnominal Adjective/Noun group.
        :param pre: Prenominal Adjective/Noun group.
        :param find: Instructs the object to find post/prenominal groupings or not.
        """
        if pre is None:
            pre = []
        self.text = sentenceText.strip()
        self.speaker = speakerData
        self.pos = []
        self.hasPair = False
        self.review = True

        if pos is None:
            global nlp
            doc = nlp(self.text)
            for token in doc:
                self.pos.append((token.text, token.pos_))
        else:
            self.pos = pos

        if post is None:
            self.postNom = []
        else:
            self.postNom = post
        if pre is None:
            self.preNom = []
        else:
            self.preNom = pre
        if find:
            self.findWords()

    def findWords(self):
        """Look of nouns and compile a list of associated adjectives."""
        # Reset the lists for regrouping.
        self.postNom = []
        self.preNom = []
        self.hasPair = False # Reset the noun/adj pair flag.
        idxMax = len(self.pos) # Maximum possible index.
        for idx in range(0, idxMax):
            w = self.pos[idx]
            if w[1] == "NOUN" and (not w[0] == '-') and (not w[1] == '_'):
                noun = w[0]
                thisPost = (noun, [])
                thisPre = (noun, [])
                # Search for adjectives.
                if idx < idxMax:
                    # Forward Search
                    if idx < idxMax - 1:
                        for x in range(idx + 1, idxMax):
                            if self.pos[x][1] == "ADJ":
                                found = True
                                self.hasPair = True
                                thisPost[1].append(self.pos[x][0])
                            else:
                                found = False
                            if not found:
                                break
                    # Backward Search
                    if idx > 0:
                        for x in range(idx - 1, -1, -1):
                            if self.pos[x][1] == "ADJ":
                                found = True
                                self.hasPair = True
                                thisPre[1].append(self.pos[x][0])
                            else:
                                found = False
                            if not found:
                                break
                    # Only add if the noun has adjectives with it.
                    if len(thisPost[1]) > 0:
                        self.postNom.append(thisPost)
                    if len(thisPre[1]) > 0:
                        self.preNom.append(thisPre)

    def dataOut(self):
        """Outputs the sentence data as a dictionary."""
        postNom = []
        preNom = []
        if len(self.postNom) > 0:
            for w in self.postNom:
                post = {
                    "noun":w[0],
                    "adjectives":w[1]
                }
                postNom.append(post)
        if len(self.preNom) > 0:
            for w in self.preNom:
                pre = {
                    "noun":w[0],
                    "adjectives":w[1]
                }
                preNom.append(pre)

        result = {
            "speaker":self.speaker.dataOut(),
            "sentence":self.text,
            "pos":self.pos,
            "postnominal":postNom,
            "prenominal":preNom
        }
        return result

    def findAdjectives(self):
        """Returns a list of all the adjectives in the sentence."""
        result = []
        for w in self.pos:
            if w[1] == "ADJ":
                result.append(w[0])
        return result

    def findBad(self):
        """Finds badly tagged words in the data, denoted by a '::' prefix.  Returns a list of such words."""
        blackList = []
        for x in range(0, len(self.pos)):
            if self.pos[x][0][:2] == "::":
                self.pos[x] = (self.pos[x][0][2:], "BAD")
                blackList.append(self.pos[x][0])
            elif self.pos[x][0] == "_" or self.pos[x][0] == "-":
                self.pos[x] = (self.pos[x][0], "BAD")

        self.findWords()
        return blackList

    def filter(self, whitelist, blacklist):
        """
        Checks the sentence for blacklisted & whitelisted adjectives and filters the data.

        :param whitelist: A list of whitelisted adjectives that if tagged as an adjective we believe.
        :param blacklist: A list of blacklisted adjectives that if tagged as an adjective we reject.
        :return: Nothing
        """
        needs_review = []
        for x in range(0, len(self.pos)):
            if self.pos[x][1] == "ADJ":
                if self.pos[x][0] in blacklist:
                    self.pos[x] = (self.pos[x][0], "BAD")
                    needs_review.append(False)
                elif self.pos[x][0] in whitelist:
                    needs_review.append(False)
                else:
                    needs_review.append(True)
            else:
                needs_review.append(False)

        self.review = False
        for rev in needs_review:
            if rev:
                self.review = True