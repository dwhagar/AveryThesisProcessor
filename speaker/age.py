import datetime

class Age:
    """A class to store the age data from a speaker."""
    def __init__(self, age_string = None):
        self.decimal = None
        self.years = None
        self.months = None
        self.days = None
        self.hours = None
        self.minutes = None
        self.seconds = None

        if not age_string is None:
            self.parse_age(age_string)

    def parse_age(self, age_str):
        # P25Y0M0DT0H0M0S
        if type(age_str) is int or type(age_str) is float:
            self.decimal = age_str
            d = datetime.timedelta(days=(self.decimal * 365))
            self.years = int(d.days / 365)
            self.months = int((d.days - (self.years * 365)) / 30)
            h = d.seconds / 60 / 60
            self.hours = int(h)
            m = (h - self.hours) * 60
            self.minutes = int(m)
            self.seconds = int(d.seconds - (self.hours * 60 * 60) - (self.minutes * 60))
        elif age_str[0] == "P":
            age_str = age_str[1:]
            age_list = age_str.split("T")
            age_date = age_list[0]

            # Not all age data has time specified, if it does not, ignore.
            if len(age_list) > 1:
                # Process the time from the age.
                age_time = age_list[1]
                temp = age_time.split("H")
                self.hours = int(temp[0][:])
                temp = temp[1].split("M")
                self.minutes = int(temp[0][:])
                temp = temp[1].split("S")
                self.seconds = int(temp[0][:])
            else:
                # If there is no time data, set all to 0.
                self.hours = 0
                self.minutes = 0
                self.seconds = 0

            # Process the date from the age.
            temp = age_date.split("Y")
            self.years = int(temp[0][:])
            temp = temp[1].split("M")
            if temp[0] == "":
                self.months = 0
            else:
                self.months = int(temp[0][:])

            # Not all age data has days specified.
            if len(temp) > 1:
                temp = temp[1].split("D")
                if temp[0] == "":
                    self.days = 0
                else:
                    self.days = int(temp[0][:])
            else:
                self.days = 0

            # Turn the individual fields into a decimal age.
            self.decimal = self.years + (self.months / 12) + (self.days / 365.25) + (self.hours / 8760) + \
                           (self.minutes / 525600) + (self.seconds / 525600 * 60)