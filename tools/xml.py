# Tools for dealing with XML data in the CEFC data set.
import os.path
import xml.etree.ElementTree as ET
from os import walk

import sentence
import speaker

from speaker import Speaker

def url_scrub(data):
    """Scrubs URL data from a line of XML text, the URL is encased in {}"""
    # This function also puts the result into all lowercase, to make pattern matching easier.
    result = data.split("}")[1]
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
                                            this_speaker = Speaker(person_ID, person_ID, person_ID, person_sex, 999, 'french')
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

def corpus_PB12(dataXML):
    """Processes Corpus Data for version PB1.2 such as the Lyon Corpus.
    Accepts input of XML data for processing and returns a list of Sentence objects.
    """
    result = [] # This will eventually store the completed list of Sentence objects.
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
        # Now for the actual transcript data.  Before this tag is reached we assume
        # that we will actually have all the speakers for this file.
        elif url_scrub(child.tag) == 'transcript':
            for u in child:
                if url_scrub(u.tag) == 'u':
                    sentenceText = "" # Full reconstructed sentence
                    thisSpeaker = None # Where to put the speaker data
                    sID = get_attribute(u, 'speaker')
                    # We need to locate this speaker in the list.
                    for s in speakers:
                        if s.sid == sID:
                            thisSpeaker = s
                    if thisSpeaker is None:
                        raise ValueError('Speaker not found in data.')
                    # We have located the speaker, now we can process the actual text.
                    for ortho in u:
                        if url_scrub(ortho.tag) == 'orthography':
                            for g in ortho:
                                noSpace = '!"#$%&\'(*+-./:;<=>?@[\\^_`{|~'
                                if url_scrub(g.tag) == 'g':
                                    # This data set is weird, each word (w) is also in a g tag.
                                    newWord = gen_sentence(g)
                                    if len(sentenceText) < 1:
                                        sentenceText = newWord
                                    elif newWord in noSpace or sentenceText[-1] in noSpace:
                                        sentenceText += newWord
                                    else:
                                        sentenceText += " " + newWord

                    # Check to make sure it is logical to append the data.
                    if not (sentenceText == "" or thisSpeaker is None):
                        result.append(sentence.Sentence(thisSpeaker, sentenceText))

    return result

def corpus_271(dataXML):
    """Processes Corpus Data for version 2.7.1 such as Palasis and MTLM.
    Accepts input of XML data for processing and returns a list of Sentence objects.
    """
    result = []
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
            elif url_scrub(chat.tag) == 'u':
                thisSpeaker = None  # Where to put the speaker data
                sID = get_attribute(chat, 'who')
                # We need to locate this speaker in the list.
                for s in speakers:
                    if s.sid == sID:
                        thisSpeaker = s
                if thisSpeaker is None:
                    raise ValueError('Speaker not found in data.')

                sentenceText = gen_sentence(chat)
                # Check to make sure it is logical to append the data.
                if not (sentenceText == "" or thisSpeaker is None):
                    result.append(sentence.Sentence(thisSpeaker, sentenceText))

    return result

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