# A processor to read XML data for Avery's corpus.

import argparse
import os.path
import xml.etree.ElementTree as ET

from speaker import speaker

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="The name of the XML file to be processed.", required=True)

    # TODO: Add ability to scan all file sin a directory.
    # TODO: Add option for output to a CSV file

    arg = parser.parse_args()

    if not os.path.isfile(arg.file):
        print("File" + arg.file + "not found.")
        return 1

    corpusTree = ET.parse(arg.file)
    corpusRoot = corpusTree.getroot()

    allParts = []

    # Process from the root down.
    for chld in corpusRoot:
        # Process the Participants
        if chld.tag == "participants":
            role = None
            name = None
            sex = None
            age = None
            lang = None

            for part in chld:
                # Gather every participant in turn.
                if part.tag == "participant":
                    sid = part.attrib['id']

                    # Gather the actual data.
                    for partData in part:
                        if partData.tag == "role":
                            role = partData.text
                        elif partData.tag == "name":
                            name = partData.text
                        elif partData.tag == "sex":
                            sex = partData.text
                        elif partData.tag == "age":
                            age = partData.text
                        elif partData.tag == "lang":
                            lang = partData.text

                    curPart = speaker.Speaker(sid, role, name, sex, age, lang)
                    allParts.append(curPart)

        # Process the actual word data, starting with the speaker.
        elif chld.tag == "transcript":
            for u in chld:
                # Provide a place to store a reference to the current speaker information.
                s = None
                # Gather the speaker from the <u> tag.
                if u.tag == "u":
                    sid = u.attribute['speaker']

                    # Now find the speaker by the ID in the list.
                    for part in allParts:
                        if part.sid == sid:
                            # When the speaker ID is found, make a reference to it.
                            s = part

                    # Now process the text via the groupTier tag under Morphology
                    for g in u:
                        if g.tag == "groupTier":
                            if g.attribute['tierName'] == "Morphology":
                                # Each word is stored in a <tg> tag and under that a <w> tag.
                                for t in g:
                                    if t.tag == "tg":
                                        for w in t:
                                            if w.tag == "w":
                                                # TODO: Parse the word string itself.
                                                print(w.text)

            # <transcript> contains all the transcript information
            # <u speaker="MOT" id="2ccada9a-8529-4241-8f9e-7a649447923e" excludeFromSearches="false">
            #   the u tag contains the groupTier and speaker data within the tag
            # <groupTier tierName="Morphology"> contains words and types

    return 0

main()

# TODO:  Remove all text after the ampersand in the data file.