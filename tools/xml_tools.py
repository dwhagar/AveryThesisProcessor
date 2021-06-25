# Tools for dealing with XML data in the CEFC data set.

import xml.etree.ElementTree as ET

from speaker import Speaker

def urlScrub(data):
    """Scrubs URL data from a line of XML text, the URL is encased in {}"""
    # This function also puts the result into all lowercase, to make pattern matching easier.
    result = data.split("}")[1]
    return result.lower()

def getAttrib(data, att):
    """Safely pulls an attribute (att) out of an XML tag input (data).
    Returns None type if attribute is now found.
    """
    result = None

    for attribute in data.attrib:
        if urlScrub(attribute) == att:
            result = data.attrib[attribute]

    return result

def read_speaker(file):
    """Reads an XML file and extract speaker data."""
    XML_tree = ET.parse(file)
    XML_root = XML_tree.getroot()

    speakers = []

    for element in XML_root:
        if urlScrub(element.tag) == 'teiheader':
            for sub_element in element:
                if urlScrub(sub_element.tag) == 'profiledesc':
                    for profile_element in sub_element:
                        if urlScrub(profile_element.tag) == 'particdesc':
                            for list_element in profile_element:
                                if urlScrub(list_element.tag) == 'listperson':
                                    for person_element in list_element:
                                        if urlScrub(person_element.tag) == 'person':
                                            # Woo!  Found a person!
                                            person_ID = getAttrib(person_element, 'id')
                                            person_sex = 'unknown'
                                            for person_data in person_element:
                                                if urlScrub(person_data.tag) == 'sex':
                                                    person_sex = person_data.text.strip()
                                                    if person_sex == 'F':
                                                        person_sex = 'female'
                                                    elif person_sex == 'M':
                                                        person_sex = 'male'
                                            this_speaker = Speaker(person_ID, person_ID, person_ID, person_sex, 999, 'french')
                                            speakers.append(this_speaker)

    return speakers