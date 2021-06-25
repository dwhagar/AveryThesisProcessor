# Tools for dealing with the ORFEO files in the CEFC data set.

from .tools import read_text

def read_sentences(file, speakers):
    """Reads sentence data from file and parses it with the speaker data."""
    bulk_data = read_text(file)

    sentences = []

    for line in bulk_data:
        if '\t' in line:
            word_data = line.split('\t')
