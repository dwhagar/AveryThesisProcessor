class Age:
    """A class to store the age data from a speaker."""
    def __init__(self, ageStr = None):
        if not ageStr is None:
            self.parseAge(ageStr)

    def parseAge(self, ageStr):
        # TODO: write function to parse the date strings
        return