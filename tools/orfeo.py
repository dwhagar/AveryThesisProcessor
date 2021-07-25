# Tools for dealing with the ORFEO files in the CEFC data set.

import os.path
from os import walk
from sentence import Sentence
from .text import read_text

def find_orfeo_files(directory):
    """From a path generates a list of all files matching ORFEO file extension."""
    result = []

    for (dirpath, dirnames, filenames) in walk(directory):
        for file in filenames:
            if file[-5:].lower() == "orfeo":
                result.append(os.path.join(dirpath, file))

    return result

def read_sentences(file, speakers):
    """Reads sentence data from file and parses it with the speaker data."""
    bulk_data = read_text(file)

    sentence_indecies = []
    sentences = []

    # Use these for index bounds of each block of sentence data.
    x = -1
    y = -1

    # Find the beginning and end indecies for each sentence block.
    for idx in range(0, len(bulk_data)):
        if len(bulk_data[idx]) > 0:
            if bulk_data[idx][0] == '1':
                x = idx
        else:
            y = idx

        if x > -1 and y > -1:
            sentence_indecies.append((x, y))
            x = -1
            y = -1

    # Use the bounds of each sentence block to extract each sentence.
    # Making the assumption that while each word has a speaker ID, all sentence
    # blocks are uttered by the same person.  This may not be true, but we
    # don't really care that much about the speaker data.
    for block in sentence_indecies:
        data_block = bulk_data[block[0]:block[1]]

        # Lets extract the speaker information.
        speaker_ID = data_block[0][-1]
        this_speaker = None
        for speaker in speakers:
            if speaker_ID == speaker.sid:
                this_speaker = speaker
                break

        this_word_list = []
        this_sentence_list = []
        for data in data_block:
            word_data = data.split('\t')
            this_word_list.append((word_data[1], word_data[3]))
            this_sentence_list.append(word_data[1])

        sentence_text = " ".join(this_sentence_list)

        this_sentence = Sentence(this_speaker, sentence_text, this_word_list)
        this_sentence.lem()

        sentences.append(this_sentence)

    return sentences