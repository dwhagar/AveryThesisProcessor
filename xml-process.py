#!/usr/bin/env python3
# A processor to read XML data for Avery's corpus.

import argparse
import os.path
from os import walk, getcwd
import xml.etree.ElementTree as ET

# Import custom class.
import speaker

def urlScrub(data):
    """Scrubs URL data from a line of XML text, the URL is encased in {}"""
    result = data.split("}")[1]
    return result

def findXML(directory, r = False):
    """Takes a directory specification and produces a list of XML files."""
    result = []

    for (dirpath, dirnames, filenames) in walk(directory):
        for file in filenames:
            if file[-3:].lower() == "xml":
                result.append(os.path.join(dirpath, file))

        if not r:
            dirnames.clear()

    return result

def genCSV(hdr, data):
    """Generate a list of CSV formatted strings from a list of statistical data."""
    result = []

    # Add header line.
    result.append(hdr)

    # Add data to file.
    for item in data:
        dataLine = ""
        for element in item:
            if len(dataLine) == 0:
                dataLine = str(element)
            else:
                dataLine += "," + str(element)
        result.append(dataLine)

    return result

def writeCSV(data, file, test = False):
    """Write CSV formatted data to a file."""
    if len(data) > 1:
        if test:
            for line in data:
                print(line)
        else:
            print("Saving CSV data to '" + file + "'.")
            f = open(file, "w")

            for line in data:
                print(line, file=f)

            f.close()
    else:
        print("No data found for '" + file + "', skipping.")

def countPairs(data, age):
    """Counts how many of a single pair is in a given list.  Returns a tuple of age, pair, and count."""
    setData = list(set(data[:]))

    result = []

    for item in setData:
        count = data.count(item)
        result.append((age, item, count))

    return result

def ageKey(val):
    """Simple function to allow sorting by the age of a speaker."""
    return val.age.years

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="The name of the XML file to be processed.")
    parser.add_argument("-d", "--dir", type=str, help="The directory name to find XML files to processed.")
    parser.add_argument("-c", "--child", type=str, help="The name of the CSV file to output the child data.",
                        default=os.path.join(getcwd(), "child.csv"))
    parser.add_argument("-a", "--adult", type=str, help="The name of the CSV file to output the adult data.",
                        default=os.path.join(getcwd(), "adult.csv"))
    parser.add_argument("-s", "--sib", type=str, help="The name of the CSV file to output the sibling data.",
                        default=os.path.join(getcwd(), "sibling.csv"))
    parser.add_argument("-j", "--preadj", type=str, help="The name of the CSV file to output the pronominal adjective pairs.",
                        default=os.path.join(getcwd(), "pre-adjectives.csv"))
    parser.add_argument("-k", "--postadj", type=str, help="The name of the CSV file to output the postnominal adjective pairs.",
                        default=os.path.join(getcwd(), "post-adjectives.csv"))
    parser.add_argument("-r", "--recursive", help="Should a directory be looked at recursively.", action='store_true')
    parser.add_argument("-t", "--test", help="Test mode, output goes to console.", action='store_true')

    arg = parser.parse_args()

    if arg.file is None and arg.dir is None:
        print("You must specify either a file or directory to process, use '-h' for help.")
        return 1

    fileList = []

    # Process any file and directory names and make a list to iterate through.
    if not arg.file is None:
        if not os.path.isfile(arg.file):
            print("File " + arg.file + " not found or is not a file.")
            return 1
        fileList.append(arg.file)
    elif not arg.dir is None:
        if not os.path.isdir(arg.dir):
            print("Directory " + arg.dir + " not found or is not a directory.")
            return 1
        fileList = findXML(arg.dir, arg.recursive)

    # Variable to store all of the speaker data for all processed participants.
    allParts = []

    # Process all the XML files in the list.
    for file in fileList:
        print("Processing file '" + file + "'...")

        corpusTree = ET.parse(file)
        corpusRoot = corpusTree.getroot()

        # Stores the list of participants unique to this file.
        fileParts = []

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
                        fileParts.append(curPart)

            # Process the actual word data, starting with the speaker.
            elif urlScrub(chld.tag) == "transcript":
                for u in chld:
                    # Provide a place to store a reference to the current speaker information.
                    s = None
                    # Gather the speaker from the <u> tag.
                    if urlScrub(u.tag) == "u":
                        sid = u.attrib['speaker']

                        # Now find the speaker by the ID in the list.
                        for part in fileParts:
                            if part.sid == sid:
                                # When the speaker ID is found, make a reference to it.
                                s = part

                        # Now process the text via the groupTier tag under Morphology
                        for g in u:
                            if urlScrub(g.tag) == "groupTier":
                                if g.attrib['tierName'] == "Morphology":
                                    # Record if a noun is seen before an adjective.
                                    seenNoun = False
                                    seenAdj = False
                                    noun = None
                                    adj = None

                                    # Each word is stored in a <tg> tag and under that a <w> tag.
                                    for t in g:
                                        if urlScrub(t.tag) == "tg":
                                            for w in t:
                                                if urlScrub(w.tag) == "w":
                                                    if not (w.text[0] == "("
                                                            or w.text[-1] == ")"
                                                            or w.text.find('|') < 0):
                                                        word = speaker.Word(w.text)
                                                        if word.noun:
                                                            seenNoun = True
                                                            noun = word
                                                        elif word.adj:
                                                            seenAdj = True
                                                            word.adj = True
                                                            adj = word
                                                            if seenNoun and not seenAdj:
                                                                word.beforeNoun = False
                                                            elif not seenNoun and seenAdj:
                                                                word.beforeNoun = True

                                                        # NOTE:  This is not the best way to do this and
                                                        #        does not handle complex sentences particularly
                                                        #        well, could provide unreliable statistics.

                                                        # TODO: Ask Avery about this problem.

                                                        # Store the noun pairs in their appropriate list.
                                                        if seenNoun and seenAdj:
                                                            if adj.beforeNoun:
                                                                s.prePairs.append((adj,noun))
                                                            else:
                                                                s.postPairs.append((adj,noun))
                                                            # Reset the flags so we don't add multiple pairs.
                                                            seenNoun = False
                                                            seenAdj = False

                                                        # Store the word into the list for this speaker.
                                                        if not word.punctuation:
                                                            s.words.append(word)

                                    # Look for adjectives without nouns (these are not used in statistics).
                                    if seenAdj and not seenNoun:
                                        s.orphans.append(adj)

        # Add all participants from this file to the master list.
        allParts.extend(fileParts)

    if len(allParts) < 1:
        print("There was an error processing the data, no participants were found.")
        return 1

    # A pair of lists to store all the statistical information before output to CSV files.
    childStats = []
    adultStats = []
    siblingStats = []

    # Gather statistics for each category of person.
    for spk in allParts:
        tmp = spk.getStats()
        if tmp[6] > 0:
            if spk.adult:
                adultStats.append(tmp)
            elif spk.sibling:
                siblingStats.append(tmp)
            else:
                childStats.append(tmp)

    # Going to copy the list as memory isn't an issue and I'd rather leave the original list intact.
    ageList = allParts[:]
    ageList.sort(key=ageKey)

    # A list to store all of the age / pair data for each group of 6 months and broken down by gender.
    prePairsM = []
    postPairsM = []
    prePairsF = []
    postPairsF = []

    # Now lets construct the CSV data from the sorted speaker list.
    maxAge = ageList[len(ageList) - 1].age.years
    ageLow = 0
    ageHigh = 0.5

    while ageHigh < maxAge:
        # A list to store word pair data, each will be stored with a line for every 6 months.
        curGroupPreM = []
        curGroupPostM = []
        curGroupPreF = []
        curGroupPostF = []

        for spk in ageList:
            # Check ages and construct some lists.
            if ageLow <= spk.age.years < ageHigh:
                tmp = spk.getPairs()

                if spk.sex == "male":
                    curGroupPreM.extend(tmp[0])
                    curGroupPostM.extend(tmp[1])
                if spk.sex == "female":
                    curGroupPreF.extend(tmp[0])
                    curGroupPostF.extend(tmp[1])

        # Construct the list of lists, including age data.
        if len(curGroupPreM) > 0:
            prePairsM.extend(countPairs(curGroupPreM, ageLow))

        if len(curGroupPostM) > 0:
            postPairsM.extend(countPairs(curGroupPostM, ageLow))

        if len(curGroupPreF) > 0:
            prePairsF.extend(countPairs(curGroupPreF, ageLow))

        if len(curGroupPostF) > 0:
            postPairsF.extend(countPairs(curGroupPostF, ageLow))

        ageLow = ageHigh
        ageHigh = ageHigh + 0.5

    # Construct the actual CSV files.
    statHeader = "Role,Name,Gender,Age (Dec),Age (Y;M),Words,Adjectives,Prenominal,% Prenominal,Prenominal Pairs,Postnominal Pairs,Orphans"
    childCSV = genCSV(statHeader, childStats)
    adultCSV = genCSV(statHeader, adultStats)
    siblingCSV = genCSV(statHeader, siblingStats)

    adjheader = "Age Lower,Pair,Count"
    adjPreMCSV = genCSV(adjheader, prePairsM)
    adjPostMCSV = genCSV(adjheader, postPairsM)
    adjPreFCSV = genCSV(adjheader, prePairsF)
    adjPostFCSV = genCSV(adjheader, postPairsF)

    # Write the CSV files.
    writeCSV(childCSV, arg.child, arg.test)
    writeCSV(adultCSV, arg.adult, arg.test)
    writeCSV(siblingCSV, arg.sib, arg.test)
    writeCSV(adjPreMCSV, arg.preadj + "-male", arg.test)
    writeCSV(adjPostMCSV, arg.postadj + "-male", arg.test)
    writeCSV(adjPreFCSV, arg.preadj + "-female", arg.test)
    writeCSV(adjPostFCSV, arg.postadj + "-female", arg.test)

    return 0

main()