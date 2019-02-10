# A processor to read XML data for Avery's corpus.

import argparse
import os.path
from os import walk
import xml.etree.ElementTree as ET

# Import custom class.
import speaker

def urlScrub(data):
    """Scrubs URL data from a line of XML text, the URL is encased in {}"""
    result = data.split("}")[1]
    return result

def findXML(dir, r = False):
    """Takes a directory specification and produces a list of XML files."""
    result = []

    for (dirpath, dirnames, filenames) in walk(dir):
        for file in filenames:
            if file[-3:].lower() == "xml":
                result.append(os.path.join(dirpath, file))

        if not r:
            dirnames.clear()

    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="The name of the XML file to be processed.")
    parser.add_argument("-d", "--dir", type=str, help="The directory name to find XML files to processed.")
    parser.add_argument("-o", "--output-child", type=str, help="The name of the CSV file to output the child data.")
    parser.add_argument("-a", "--output-adult", type=str, help="The name of the CSV file to output the adult data.")
    parser.add_argument("-r", "--recursive", type=bool, help="Should a directory be looked at recursively.")

    arg = parser.parse_args()

    if arg.file == "" and arg.dir == "":
        print("You must specify either a file or directory to process.")
        return 1

    fileList = []

    # Process any file and directory names and make a list to iterate through.
    if not arg.file == "":
        if not os.path.isfile(arg.file):
            print("File " + arg.file + " not found or is not a file.")
            return 1
        fileList.append(arg.file)
    elif not arg.dir == "":
        if not os.path.isdir(arg.dir):
            print("Directory " + arg.dir + " not found or is not a directory.")
            return 1
        fileList = findXML(dir, arg.recursive)

    # Process all the XML files in the list.
    for file in fileList:
        print("Processing file " + file + "...")

        corpusTree = ET.parse(arg.file)
        corpusRoot = corpusTree.getroot()

        allParts = []

        # Process from the root down.
        for chld in corpusRoot:
            # Process the Participants
            if urlScrub(chld.tag) == "participants":
                role = None
                name = None
                sex = None
                age = None
                lang = None

                for part in chld:
                    # Gather every participant in turn.
                    if urlScrub(part.tag) == "participant":
                        sid = part.attrib['id']

                        # Gather the actual data.
                        for partData in part:
                            if urlScrub(partData.tag) == "role":
                                role = partData.text
                            elif urlScrub(partData.tag) == "name":
                                name = partData.text
                            elif urlScrub(partData.tag) == "sex":
                                sex = partData.text
                            elif urlScrub(partData.tag) == "age":
                                age = partData.text
                            elif urlScrub(partData.tag) == "language":
                                lang = partData.text

                        curPart = speaker.Speaker(sid, role, name, sex, age, lang)
                        allParts.append(curPart)

            # Process the actual word data, starting with the speaker.
            elif urlScrub(chld.tag) == "transcript":
                for u in chld:
                    # Provide a place to store a reference to the current speaker information.
                    s = None
                    # Gather the speaker from the <u> tag.
                    if urlScrub(u.tag) == "u":
                        sid = u.attrib['speaker']

                        # Now find the speaker by the ID in the list.
                        for part in allParts:
                            if part.sid == sid:
                                # When the speaker ID is found, make a reference to it.
                                s = part

                        # Now process the text via the groupTier tag under Morphology
                        for g in u:
                            if urlScrub(g.tag) == "groupTier":
                                if g.attrib['tierName'] == "Morphology":
                                    # Record if a noun is seen before an adjective.
                                    seenNoun = False

                                    # Each word is stored in a <tg> tag and under that a <w> tag.
                                    for t in g:
                                        if urlScrub(t.tag) == "tg":
                                            for w in t:
                                                if urlScrub(w.tag) == "w":
                                                    if not (w.text[0] == "(" or w.text[-1] == ")"):
                                                        word = speaker.Word(w.text)
                                                        if word.noun:
                                                            seenNoun = True
                                                        elif word.adj:
                                                            word.adj = True
                                                            if seenNoun:
                                                                word.beforeNoun = False
                                                            else:
                                                                word.beforeNoun = True

                                                        # Store the word into the list for this speaker.
                                                        if not word.punctuation:
                                                            s.words.append(word)

    if len(allParts) < 1:
        print("There was an error processing the data, no participants were found.")
        return 1

    for spk in allParts:
        continue

    return 0

main()