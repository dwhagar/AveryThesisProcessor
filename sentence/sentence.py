import nltk

class Sentence:
    """Storage of a sentence and other data from a corpus."""
    def __init__(self, speakerData, sentenceText):
        """
        Stores data for a single sentence.
        :param speakerData: A Speaker object denoting who uttered the sentence.
        :param sentenceText: The actual text of the sentence.
        """
        self.text = sentenceText
        self.speaker = speakerData
        self.pos = nltk.pos_tag(nltk.word_tokenize(sentenceText))