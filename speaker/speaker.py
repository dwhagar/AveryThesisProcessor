from .age import Age

class Speaker:
    """A class to store information about a speaker."""
    def __init__(self, sid = None, role = None, name = None, sex = None, age = None, language = None):
        self.sid = sid.strip()
        self.role = role.replace("_", " ").strip()
        # Some names are not filled in, replace with the role of the person.
        if name is None:
            name = self.role
        self.name = name.strip()
        if not sex is None:
            self.sex = sex.strip()
        else:
            self.sex = "unknown"
        if not language is None:
            self.language = language.strip()
        self.adult = False
        self.sibling = False

        if not age is None:
            self.age = Age(age)
            if self.age.decimal >= 18:
                self.adult = True
        else:
            self.age = Age(999)
            self.adult = True

        if self.sid == "BRO" or self.sid == "SIS":
            self.sibling = True

    def check_speaker(self, speaker_data):
        """Checks to see if a Speaker is the same as this Speaker."""
        if speaker_data.role == self.role\
                and speaker_data.name == self.name\
                and speaker_data.age.decimal == self.age.decimal\
                and speaker_data.sex == self.sex:
            return True
        else:
            return False

    def data_out(self):
        """Output the data as a dictionary."""
        result = {
            "sid":self.sid,
            "role":self.role,
            "name":self.name,
            "sex":self.sex,
            "adult":self.adult,
            "lang":self.language,
            "age":self.age.decimal
        }
        return result

def match_speaker(speaker_list, speaker_ID):
    """
    Checks for a speaker ID against a list of Speaker objects and returns the matching
    Speaker object, or None Type if not found.

    :param speaker_list: A list of Speaker objects to search
    :param speaker_ID: The ID of the speaker being looked for
    :return: A Speaker object matching the ID or None Type if not found
    """
    result = None

    for s in speaker_list:
        if s.sid == speaker_ID:
            result = s
            break

    return result