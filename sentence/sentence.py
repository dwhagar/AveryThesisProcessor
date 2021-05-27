# This goes contrary how how the spacy docs say one should install the corpus data.
# Loading takes a long time, so we define it as a global variable so it doesn't have
# to load with each and every sentence.

# We had some issues with this because of it being loaded on a mac in a virtual
# environment for PyCharm.  This is not the standard way to load the french data for
# the parts of speech (POS) tagger.
import fr_core_news_lg
import string
nlp = fr_core_news_lg.load()
from french_lefff_lemmatizer.french_lefff_lemmatizer import FrenchLefffLemmatizer
# Similar to above with defining a global object to reduce run times for loading.
# The lemmatizer object takes a while to load, so loading it as a global object.
lemmatizer = FrenchLefffLemmatizer()

class Sentence:
    """Storage of a sentence and other data from a corpus."""
    def __init__(self, speaker_data, sentence_text, pos = None, post = None, pre = None, find = True):
        """
        Stores data for a single sentence.
        :param speaker_data: A Speaker object denoting who uttered the sentence.
        :param sentence_text: The actual text of the sentence.
        :param pos: Pre-tagged POS data.
        :param post: Postnominal Adjective/Noun group.
        :param pre: Prenominal Adjective/Noun group.
        :param find: Instructs the object to find post/prenominal groupings or not.
        """
        self.text = sentence_text.strip()
        self.speaker = speaker_data
        self.pos = []

        self.has_pair = False
        # This automatically sets to true, but is a holdover from a previous stage in the data.
        # as of October 5, 2020 all sentence data has been verified.
        self.review = True

        # If we already have parts of speech, load them.
        if pos is None:
            global nlp
            doc = nlp(self.text)
            for token in doc:
                self.pos.append((token.text, token.pos_))
        else:
            self.pos = pos

        # If we already have the prenominal and postnominal lists, load them.
        if post is None:
            self.post_nom = []
        else:
            self.post_nom = post
            self.has_pair = True
        if pre is None:
            self.pre_nom = []
        else:
            self.pre_nom = pre
            self.has_pair = True

        # If we want to go through the find process again, do it.
        if find:
            self.find_words()

    def sanitize_sentence(self):
        """Goes through the sentence data and makes sure it is sane"""
        sentence_list = self.text.split()
        sentence_new = []

        # This is only really needed to sync up the sentence text with the parts
        # of speech and thus with the pernominal / postnominal lists.
        # Note that we don't strip the "." off the end here but we do for the
        # parts of speech word list -- IF it is contained at the end of a word.
        for word in sentence_list:
            if len(word) > 0:
                if word[-2:] == "}." or word[-2:] == ":}":
                    word = word[:-2]
            if len(word) > 0:
                if word[-1] == "}":
                    word = word[:-1]
            if len(word) > 0:
                if word[0] == "{":
                    if len(word) == 1:
                        word = ""
                    else:
                        word = word[1:]
            # This is for some special cases such as "chaise+lounge" where chaise
            # is a noun and lounge is an adjective.
            if word.find("+") > -1:
                new_words = word.split("+")
                sentence_new.extend(new_words)
            elif word.find("{") > -1:
                new_words = word.split("{")
                sentence_new.extend(new_words)
            else:
                sentence_new.append(word)

        self.text = " ".join(sentence_new)

    def sanitize_words(self):
        """Goes through the words and makes them sane."""
        new_pos = []

        # Still some problems with punctuation, this should clear it up.
        for word in self.pos:
            new_word = word[0]
            new_part = word[1]
            if not new_part == "PUNCT":
                if len(new_word) > 0:
                    if new_word[-2:] == "}." or new_word[-2:] == ":}":
                        new_word = new_word[:-2]
                if len(new_word) > 0:
                    if new_word[-1] == "}" or new_word[-1] == ".":
                        new_word = new_word[:-1]
                if len(new_word) > 0:
                    if new_word[0] == "{":
                        if len(new_word) == 1:
                            new_word = ""
                            new_part = "BAD"
                        else:
                            new_word = new_word[1:]
                else:
                    new_part = "BAD"

                if len(new_word) < 1:
                    new_part = "BAD"

                # There is a special case, mentioned in the sanitize_sentence
                # method where two words of the types we're looking for are
                # separated by a +, in this case we cannot make too many assumptions
                # and need to be specific to what is in the data.
                if new_word == "chaise+lounge":
                    # This is structured strangely to make the rest of the function
                    # behave the way it should with minimal editing.
                    # Add the new word to the POS list in the correct place.
                    new_pos.append(("chaise", "NOUN"))
                    # The new_word and new_part variables will be added to the list
                    # once out of this if/then/else block.
                    new_word = "lounge"
                    new_part = "ADJ"
                if new_word == "mécanique{elle":
                    new_pos.append(("mécanique","ADJ"))
                    new_word = "elle"
                    new_part = "PRON"
                if new_word == "rouge{pour":
                    new_pos.append(("rouge", "ADJ"))
                    new_word = "pour"
                    new_part = "ADP"

            new_pos.append((new_word, new_part))

        self.pos = new_pos
        # Since the POS is changed, automatically redo the prenominal and postnominal.
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
            if w[1] == "NOUN" and not (w[0] == '-' or w[1] == '_' or w[0] == '>' or w[0] == '<'):
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

    def data_out_helper(self, data):
        """
        Builds a proper dictionary object for output from the prenominal and postnominal
        noun / adjective groups.

        :param data: A list of noun/adjective groups either in (noun, [adjective, ajective], lemma)
        format or (noun, [(adjcetive, root), (adjective lemma)], lemma) format.
        :return: Returns a dictionary object with all the data.
        """
        result = []
        for w in data:
            if type(w[1][0]) is tuple:
                adj_list = []
                for a in w[1]:
                    adj = {
                        "adjective": a[0],
                        "lemma": a[1]
                    }
                    adj_list.append(adj)
                group = {
                    "noun": w[0],
                    "adjectives": adj_list,
                    "lemma": w[2]
                }
            else:
                group = {
                    "noun": w[0],
                    "adjectives": w[1]
                }
            result.append(group)

        return result

    def data_out(self):
        """Outputs the sentence data as a dictionary."""
        post_nom = []
        pre_nom = []

        if len(self.post_nom) > 0:
            post_nom = self.data_out_helper(self.post_nom)
        if len(self.pre_nom) > 0:
            pre_nom = self.data_out_helper(self.pre_nom)

        result = {
            "speaker":self.speaker.data_out(),
            "sentence":self.text,
            "pos":self.pos,
            "postnominal":post_nom,
            "prenominal":pre_nom
        }
        return result

    def find_adjectives_helper(self, data):
        """
        Generates a list of adjectives and the lemma forms from the prenominal and
        postnominal lists.

        :param data: A list of adjectives grouped with a noun in the format of
        [(noun, [(adjective, lemma), (adjective, lemma)]), (noun, [(adjective, lemma), (adjective, lemma)])]
        :return: Two lists in the format of (adjectives, lammas)
        """
        adjective_list = []
        lemma_list = []

        for group in data:
            for adj in group[1]:
                adjective_list.append(adj[0].lower())
                lemma_list.append(adj[1].lower())

        return adjective_list, lemma_list

    def find_adjectives(self):
        """
        Gets a list of adjectives and lemmas from the prenominal / postnominal groups.

        :return: Two lists in the format of (adjectives, lemmas)
        """

        adj1, lemma1 = self.find_adjectives_helper(self.pre_nom)
        adj2, lemma2 = self.find_adjectives_helper(self.post_nom)

        adjectives = adj1
        adjectives.extend(adj2)
        lemmas = lemma1
        lemmas.extend(lemma2)

        return adjectives, lemmas

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

    def filter_all(self, blacklist):
        """
        Filters all words based on a blacklist of things that are NEVER words.

        :param blacklist: The non-word blacklist as a list of strings.
        :return: None
        """

        # More data issues
        for x in range(0, len(self.pos)):
            if self.pos[x][0] in blacklist or \
                    self.pos[x][0] in string.digits or \
                    self.pos[x][0] in string.punctuation:
                self.pos[x] = (self.pos[x][0], "BAD")

        # Remove BAD Words
        remove_list = []    # Need to avoid bad index errors when removing.
        for x in range(0, len(self.pos)):
            if self.pos[x][1] == "BAD":
                remove_list.append(self.pos[x])

        # Annoying crap that is needed to get past bad index errors.
        for item in remove_list:
            self.pos.remove(item)

        # Reconstitute sentence
        new_sentence_list = []
        for word in self.pos:
            new_sentence_list.append(word[0])

        self.text = " ".join(new_sentence_list)

        self.find_words()
        self.lem()

    def lem_helper(self, data):
        """
        Processes a list of noun / adjectives tuples and returns a list that includes the lemmatized
        adjectives.

        :param data: A tuple in the format of (noun, adjectives)
        :return: A tuple in the format of (noun, adjectives) with the adjectives list in the format
        of [(adjective, lemma), (adjective, lemma)]
        """
        global lemmatizer
        new_data = []

        n_root = ""

        for w in data:
            adj_list = []
            n = w[0]

            for a in w[1]:
                # Some translation is needed.  Just going to do a chain if/elif/else for now, may use
                # something more robust later if required.
                if a.lower() == "tits":
                    a_root = "petit"
                elif a.lower() == "deux}{deux":
                    a = "deux deux"
                    a_root = "deux"
                elif a.lower() == "deu":
                    a = "deux"
                    a_root = "deux"
                elif a.lower() == "rouge}pour":
                    a = "rouge"
                    a_root = "rouge"
                elif a.lower() == "rase":
                    a_root = "rad"
                elif a.lower() == "des::petits":
                    a = "petits"
                    a_root = "petit"
                elif a.lower() == "roux":
                    a = "roux"
                    a_root = "rouge"
                else:
                    a_root = lemmatizer.lemmatize(a, 'a')

                n_root = lemmatizer.lemmatize(n, 'n')

                adj_list.append((a, a_root))
            new_data.append((n, adj_list, n_root))

        return new_data

    def lem(self):
        """
        Processes the prenominal and postnominal data to add the root form of every word present.
        This will replace the current prenominal and postnominal tuples with new ones with the
        adjective root forms.

        :return: Nothing
        """
        if len(self.pre_nom) > 0:
            self.pre_nom = self.lem_helper(self.pre_nom)
        if len(self.post_nom) > 0:
            self.post_nom = self.lem_helper(self.post_nom)

    def get_pre_post_helper(self, data):
        """
        Processes a given list of noun/adjective groups and returns a list of
        all the adjective lemmas used.

        :return: A list of all the adjective lemmas.
        """
        result = []
        for d in data:
            for a in d[1]:
                result.append(a[1])

        return result

    def get_pre_post_lists(self):
        """
        Produces a list of adjective lemmas for the pre and post nominal positions.

        :return: Returns a list of adjectives present in the format of (prenominal, postnominal)
        """
        prenom_lemmas = self.get_pre_post_helper(self.pre_nom)
        postnom_lemmas = self.get_pre_post_helper(self.post_nom)

        return prenom_lemmas, postnom_lemmas

    def get_colors_helper(self, data):
        """
        Processes a given set of noun/adjective groups and extracts those which represent colors.

        :param data: A list of noun/adjective groups that has been lemmatized.
        :return: A list of color adjectives found.
        """
        result = []

        colors = ["vert", "bleu", "blanc", "jaune", "rose", "noir", "rouge", "orange", "violet", "gris"]

        for w in data:
            for a in w[1]:
                if a[1].lower() in colors:
                    result.append(a[1].lower())

        return result

    def get_colors(self):
        """
        Processes the prenominal and postnominal noun/adjective groups and passes on only those which
        contain colors.

        :return: A list of prenominal and postnominal noun/adjective groups containing colors in the
        format of (prenominal, postnominal).
        """
        pre_nom_list = self.get_colors_helper(self.pre_nom)
        post_nom_list = self.get_colors_helper(self.post_nom)

        return pre_nom_list, post_nom_list

    def get_nouns_helper(self, data):
        """
        Gets the lemmatized noun from each noun/adjective grouping provided in the list data.

        :param data: A lemmatized list of noun/adjective groups.
        :return: All lemmatized nouns present as a list.
        """
        result = []

        for w in data:
            if not (w[2] == '<' or w[2] == '>'):
                result.append(w[2].lower())

        return result

    def get_nouns(self):
        """
        Gets the list of lemmatized nouns from prenominal/postnominal noun/adjective groups.

        :return: All lemmatized nouns present in prenominal/postnominal noun/adjective groups
        as two lists in the format of (prenominal/postnominal).
        """
        pre_nom_nouns = self.get_nouns_helper(self.pre_nom)
        post_nom_nouns = self.get_nouns_helper(self.post_nom)

        return pre_nom_nouns, post_nom_nouns

    def adj_exist_helper(self, adj, data):
        """
        Accepts an adjective lemma and a list of adjective/noun groups to check.  If found it
        returns the lemmatized noun associated with that group.  If no result is found, it returns
        "0".

        :param adj: An adjective lemma
        :param data: A list of adjective/noun groups with lemmas
        :return: If adjective lemma is found returns the lemmas for any associated nouns as a list
        """
        nouns = []

        for n in data:
            for w in n[1]:
                if w[1].lower() == adj.lower():
                    nouns.append(n[2])

        return nouns

    def adj_exist(self, adj):
        """
        Goes through all of the prenominal / postnominal adjective noun groups and returns a list
        of associated noun lemmas.

        :param adj: An adjective lemma
        :return: Two lists, one of prenominal and the other of postnominal nouns for the given
        adjective.
        """
        prenominal = self.adj_exist_helper(adj, self.pre_nom)
        postnominal = self.adj_exist_helper(adj, self.post_nom)

        return prenominal, postnominal