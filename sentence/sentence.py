# This goes contrary how how the spacy docs say one should install the corpus data.
# Loading takes a long time, so we define it as a global variable so it doesn't have
# to load with each and every sentence.
import fr_core_news_lg
nlp = fr_core_news_lg.load()

class Sentence:
    """Storage of a sentence and other data from a corpus."""
    def __init__(self, speakerData, sentenceText):
        """
        Stores data for a single sentence.
        :param speakerData: A Speaker object denoting who uttered the sentence.
        :param sentenceText: The actual text of the sentence.
        """
        self.text = sentenceText.strip()
        print(self.text)
        self.speaker = speakerData
        self.pos = []

        global nlp
        doc = nlp(self.text)
        for token in doc:
            self.pos.append((token.text, token.pos_))