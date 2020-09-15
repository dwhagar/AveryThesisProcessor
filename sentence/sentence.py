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
        idxMax = len(self.pos) # Maximum possible index.
        for idx in range(0, idxMax):
            w = self.pos[idx]
            if w[1] == "NOUN":
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

    def findBad(self):
        """Finds badly tagged words in the data, denoted by a '::' prefix.  Returns a list of such words."""
        blackList = []
        for w in self.pos:
            if w[0][:2] == "::":
                w[1] = "BAD"
                w[0] = w[0][2:]
                blackList.append(w[0])
            elif w[0] == "_" or w[0] == "-":
                w[1] = "BAD"

        self.findWords()
        return blackList