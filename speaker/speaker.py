from .age import Age

class Speaker:
    """A class to store information about a speaker."""
    def __init__(self, sid = None, role = None, name = None, sex = None, age = None, language = None):
        self.sid = sid
        self.role = role.replace("_", " ")
        self.name = name
        self.sex = sex
        self.language = language
        self.adult = False
        self.sibling = False

        if not age is None:
            self.age = Age(age)
        else:
            self.age = None

        if self.age.decimal >= 18:
            self.adult = True

        if self.sid == "BRO" or self.sid == "SIS":
            self.sibling = True

    def checkSpeaker(self, role, name, ageData, sex):
        """
        Checks to see if a speaker is the same as the one in this object.
        :param role: Role of the speaker as identified in the corpus.
        :param name: Name of the speaker as identified in the corpus.
        :param ageData: Age of the speaker as identified in the corpus.
        :param sex: Gender of the speaker as identified in the corpus.
        :return: True if the data matches this speaker, false otherwise.
        """
        if role == self.role and name == self.name and ageData.decimal == self.age.decimal :
            return True
        else:
            return False