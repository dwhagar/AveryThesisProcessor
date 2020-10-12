# This goes contrary how how the spacy docs say one should install the corpus data.
# Loading takes a long time, so we define it as a global variable so it doesn't have
# to load with each and every sentence.
import fr_core_news_lg
nlp = fr_core_news_lg.load()
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer

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
        self.has_pair = False
        self.review = True

        if pos is None:
            global nlp
            doc = nlp(self.text)
            for token in doc:
                self.pos.append((token.text, token.pos_))
        else:
            self.pos = pos

        if post is None:
            self.post_nom = []
        else:
            self.post_nom = post
        if pre is None:
            self.pre_nom = []
        else:
            self.pre_nom = pre
        if find:
            self.find_words()

    def find_words(self):
        """Look of nouns and compile a list of associated adjectives."""
        # Reset the lists for regrouping.
        self.post_nom = []
        self.pre_nom = []
        self.has_pair = False # Reset the noun/adj pair flag.
        idx_max = len(self.pos) # Maximum possible index.
        for idx in range(0, idx_max):
            w = self.pos[idx]
            if w[1] == "NOUN" and (not w[0] == '-') and (not w[1] == '_'):
                noun = w[0]
                this_post = (noun, [])
                this_pre = (noun, [])
                # Search for adjectives.
                if idx < idx_max:
                    # Forward Search
                    if idx < idx_max - 1:
                        for x in range(idx + 1, idx_max):
                            if self.pos[x][1] == "ADJ":
                                found = True
                                self.has_pair = True
                                this_post[1].append(self.pos[x][0])
                            else:
                                found = False
                            if not found:
                                break
                    # Backward Search
                    if idx > 0:
                        for x in range(idx - 1, -1, -1):
                            if self.pos[x][1] == "ADJ":
                                found = True
                                self.has_pair = True
                                this_pre[1].append(self.pos[x][0])
                            else:
                                found = False
                            if not found:
                                break
                    # Only add if the noun has adjectives with it.
                    if len(this_post[1]) > 0:
                        self.post_nom.append(this_post)
                    if len(this_pre[1]) > 0:
                        self.pre_nom.append(this_pre)

    def dataOut(self):
        """Outputs the sentence data as a dictionary."""
        post_nom = []
        pre_nom = []
        if len(self.post_nom) > 0:
            for w in self.post_nom:
                post = {
                    "noun":w[0],
                    "adjectives":w[1]
                }
                post_nom.append(post)
        if len(self.pre_nom) > 0:
            for w in self.pre_nom:
                pre = {
                    "noun":w[0],
                    "adjectives":w[1]
                }
                pre_nom.append(pre)

        result = {
            "speaker":self.speaker.dataOut(),
            "sentence":self.text,
            "pos":self.pos,
            "postnominal":post_nom,
            "prenominal":pre_nom
        }
        return result

    def find_adjectives(self):
        """Returns a list of all the adjectives in the sentence."""
        result = []
        for w in self.pos:
            if w[1] == "ADJ":
                result.append(w[0])
        return result

    def find_bad(self):
        """Finds badly tagged words in the data, denoted by a '::' prefix.  Returns a list of such words."""
        black_list = []
        for x in range(0, len(self.pos)):
            if self.pos[x][0][:2] == "::":
                self.pos[x] = (self.pos[x][0][2:], "BAD")
                black_list.append(self.pos[x][0])
            elif self.pos[x][0] == "_" or self.pos[x][0] == "-":
                self.pos[x] = (self.pos[x][0], "BAD")

        self.find_words()
        return black_list

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

    def lem_helper(self, data):
        """
        Processes a list of noun / adjectives tuples and returns a list that includes the lemmatized
        adjectives.

        :param data: A tuple in the format of (noun, adjectives)
        :return: A tuple in the format of (noun, adjectives) with the adjectives list in the format
        of [(adjective, root), (adjective, root)]
        """
        lemmatizer = FrenchLefffLemmatizer()
        new_data = []
        for w in data:
            adj_list = []
            n = w[0]
            for a in w[1]:
                a_root = lemmatizer.lemmatize(a, 'a')
                adj_list.append((a, a_root))
            new_data.append((n, adj_list))

        return new_data

    def lem(self):
        """
        Processes the prenominal and postnominal data to add the root form of every word present.
        This will replace the current prenominal and postnominal tuples with new ones with the
        adjective root forms.

        :return: Nothing
        """
        self.pre_nom = self.lem_helper(self.pre_nom)
        self.post_nom = self.lem_helper(self.post_nom)
