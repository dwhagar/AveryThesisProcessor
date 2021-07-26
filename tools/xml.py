# Tools for dealing with XML data in the CEFC data set.
import os.path
import xml.etree.ElementTree as ET
from talkbank_parser import MorParser, prettyUtterance
from os import walk

import sentence
import speaker
from . import fd

def url_scrub(data):
    """Scrubs URL data from a line of XML text, the URL is encased in {}"""
    # This function also puts the result into all lowercase, to make pattern matching easier.
    if data.find("}") >= 0:
        result = data.split("}")[1]
    else:
        result = data

    return result.lower()

def get_attribute(data, att):
    """Safely pulls an attribute (att) out of an XML tag input (data).
    Returns None type if attribute is now found.
    """
    result = None

    for attribute in data.attrib:
        if url_scrub(attribute) == att:
            result = data.attrib[attribute]

    return result

def read_speaker(file):
    """Reads an XML file and extract speaker data."""
    XML_tree = ET.parse(file)
    XML_root = XML_tree.getroot()

    speakers = []

    for element in XML_root:
        if url_scrub(element.tag) == 'teiheader':
            for sub_element in element:
                if url_scrub(sub_element.tag) == 'profiledesc':
                    for profile_element in sub_element:
                        if url_scrub(profile_element.tag) == 'particdesc':
                            for list_element in profile_element:
                                if url_scrub(list_element.tag) == 'listperson':
                                    for person_element in list_element:
                                        if url_scrub(person_element.tag) == 'person':
                                            # Woo!  Found a person!
                                            person_ID = get_attribute(person_element, 'id')
                                            person_sex = 'unknown'
                                            for person_data in person_element:
                                                if url_scrub(person_data.tag) == 'sex':
                                                    person_sex = person_data.text.strip()
                                                    if person_sex == 'F':
                                                        person_sex = 'female'
                                                    elif person_sex == 'M':
                                                        person_sex = 'male'
                                            this_speaker = speaker.Speaker(person_ID, person_ID, person_ID, person_sex, 999, 'french')
                                            speakers.append(this_speaker)

    return speakers

def find_XML(directory, r = False):
    """Takes a directory specification and produces a list of XML files."""
    result = []

    for (dirpath, dirnames, filenames) in walk(directory):
        for file in filenames:
            if file[-3:].lower() == "xml":
                result.append(os.path.join(dirpath, file))

        if not r:
            dirnames.clear()

    return result

def process_XML(file):
    """
    Processes XML data using the talkbank_parser library.

    :param file: Name of the file to be read.
    :return: A list of FD objects read from the XML file.
    """
    # The MorParser does not actually extract the speaker information that is needed such as,
    # age and gender, will have to extract that ourselves.
    these_speakers = process_speakers(file)

    parser = MorParser()
    corpus = parser.parse(file)
    corpus = list(corpus) # Generate a list of utterances with their appropriate speaker information.

    data = []

    # Go through and build the data structure for the Sentence object.
    for item in corpus:
        uid, speaker_ID, utterance = item
        this_speaker = speaker.match_speaker(these_speakers, speaker_ID)
        this_sentence = None
        sentence_text = ""
        if not(this_speaker is None):
            word_list = [] # List of raw words to build the sentence text.
            pos_list = [] # List of words with parts of speech.
            for word in utterance:
                word_list.append(word.word)
                pos_list.append((word.word, word.pos))
                sentence_text = " ".join(word_list)

            this_sentence = sentence.Sentence(this_speaker, sentence_text, pos_list)

        if not(this_sentence is None):
            data.append(fd.FD(file, this_sentence))

    return data

def process_speakers(file):
    """
    Reads speaker information out of an XML file and returns a list of Speaker objects.

    :param file: Filename of the file to be read.
    :return: A list of Speaker objects identified in the file.
    """
    corpusTree = ET.parse(file)
    corpusRoot = corpusTree.getroot()

    speakers = [] # All speakers found in a particular file.

    # Need to determine file version for processing, since different files have
    # different capitalization, we need to account for that.
    ver = get_attribute(corpusRoot, 'version')
    if ver is None:
        ver = get_attribute(corpusRoot, 'Version')

    # Now branch to the proper processor.
    if ver == 'PB1.2':
        speakers = corpus_PB12(corpusRoot)
    elif ver == '2.7.1':
        speakers = corpus_271(corpusRoot)

    return speakers

def corpus_PB12(dataXML):
    """
    Processes version PB1.2 of the XML data to extract speaker data.

    :param dataXML: XML Tree
    :return:  A list of Speaker Objects
    """
    speakers = []

    for child in dataXML:
        # Process participants to get participant IDs and build speakers.
        if url_scrub(child.tag) == 'participants':
            for part in child:
                if url_scrub(part.tag) == 'participant':
                    sID = get_attribute(part, 'id')
                    if sID is None:
                        raise ValueError("Something went wrong with the speaker data, no speaker ID found.")
                    sRole = None
                    sName = None
                    sSex = None
                    sAge = None
                    sLang = None
                    for partData in part:
                        if url_scrub(partData.tag) == 'role':
                            sRole = partData.text
                        elif url_scrub(partData.tag) == 'name':
                            sName = partData.text
                        elif url_scrub(partData.tag) == 'sex':
                            sSex = partData.text
                        elif url_scrub(partData.tag) == 'age':
                            sAge = partData.text
                        elif url_scrub(partData.tag) == 'language':
                            sLang = partData.text
                    speakers.append(speaker.Speaker(sID, sRole, sName, sSex, sAge, sLang))

    return speakers

def corpus_271(dataXML):
    """
    Processes version 2.7.1 of the XML data to extract speaker data.

    :param dataXML: XML Tree
    :return:  A list of Speaker Objects
    """
    speakers = []

    if url_scrub(dataXML.tag) == 'chat':
        for chat in dataXML:
            # First thing to look for in the chat tag is the list of participants.
            if url_scrub(chat.tag) == 'participants':
                # Each participant is listed as an attribute of the participant tag.
                for parts in chat:
                    # Now get all the information about a participant from the tag.
                    if url_scrub(parts.tag) == 'participant':
                        sID = get_attribute(parts, 'id')
                        sName = get_attribute(parts, 'name')
                        sRole = get_attribute(parts, 'role')
                        sLang = get_attribute(parts, 'language')
                        sAge = get_attribute(parts, 'age')
                        sSex = get_attribute(parts, 'sex')
                        # Generate the Speaker and add to the list of speakers.
                        speakers.append(speaker.Speaker(sID, sRole, sName, sSex, sAge, sLang))

    return speakers

def gen_sentence(dataXML):
    """Takes the w tags for words from a sentence transcript and returns the sentence
    as a string or None if no w tags are found.
    """
    result = ""
    noSpace = '!"#$%&\'(*+-./:;<=>?@[\\^_`{|~'
    for w in dataXML:
        if url_scrub(w.tag) == 'w':  # Words
            if not (w.text == "" or w.text is None):  # Ignore empty text.
                if len(result) < 1:
                    result = w.text
                elif w.text in noSpace or result[-1] in noSpace:
                    result += w.text
                else:
                    result += " "
                    result += w.text
        elif url_scrub(w.tag) == 'p':  # Punctuation
            if not (w.text == "" or w.text is None):  # Ignore empty text.
                if len(result) < 1:
                    result = w.text
                else:
                    result += w.text

    return result