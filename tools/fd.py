# File data object for loading corpus data.

class FD:
    def __init__(self, file, s):
        """
        Stores the sentence and the file name the sentence came from.

        :param file: Name of the original file.
        :param s: Sentence object to be stored.
        """
        self.file = file
        self.sentence = s

    def data_out(self):
        """Processes the file / sentence data into a dictionary for JSON output."""
        result = {
            "file":self.file,
            "data":self.sentence.data_out()
        }

        return result