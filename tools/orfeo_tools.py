# Tools for dealing with the ORFEO files in the CEFC data set.

from .tools import read_text

def read_sentences(file, speakers):
    """Reads sentence data from file and parses it with the speaker data."""
