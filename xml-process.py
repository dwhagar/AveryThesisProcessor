# A processor to read XML data for Avery's corpus.

import argparse
import os.path
import xml.etree.ElementTree as ET

from speaker import speaker

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="The name of the XML file to be processed.", required=True)
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

    return 0

main()