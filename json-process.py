#!/usr/bin/env python3
# A processor to read JSON data for Avery's corpus.
import argparse
import os.path
from os import getcwd
import json

# Import custom classes.
import speaker
import sentence

class file_data:
    def __init__(self, file, s):
        """
        Stores the sentence and the file name the sentence came from.

        :param file: Name of the original file.
        :param s: Sentence object to be stored.
        """
        self.file = file
        self.sentence = s

def save_text(data, file):
    """
    Writes the data to the file as a text file.

    :param data: List data to be saved.
    :param file: File to save data to.
    :return: None
    """
    for i in range(0, len(data)):
       data[i] = data[i] + '\n'

    f = open(file, 'w')
    f.writelines(data)
    f.close()

def read_text(file):
    """
    Reads text data from a file, one list item per line.

    :param file: File to read data from.
    :return: List of data items from the file.
    """
    result = []
    if os.path.isfile(file):
        f = open(file, 'r')
        data = f.readlines()
        f.close()

        for d in data:
            d = d.strip('\n')
            d = d.strip()
            result.append(d)

    return result

def save_JSON(data, file):
    """
    Saves sentence / file data to a JSON file.

    :param data: List of file_data objects to be saved
    :param file: File to save objects to
    :return: None
    """
    outData = []

    for d in data:
        jsonData = {
            "file":d.file,
            "data":d.sentence.data_out()
        }
        if d.sentence.has_pair:
            outData.append(jsonData)

    with open(file, 'w') as f:
        json.dump(outData, f, indent=4, ensure_ascii=False)

def read_JSON(file):
    """
    Reads data into memory from a JSON file.

    :param file: File to read from.
    :return: A list of file_data objects containing sentence data and original file names.
    """
    # Load JSON file.
    with open(file) as json_file:
        data = json.load(json_file)

    sentences = [] # List of all the sentences by file.
    for d in data:
        data_JSON = d['data']
        if not data_JSON['sentence'][:2] == "::":
            sp_JSON = data_JSON['speaker']
            sp = speaker.Speaker(sp_JSON['sid'],
                                 sp_JSON['role'],
                                 sp_JSON['name'],
                                 sp_JSON['sex'],
                                 float(sp_JSON['age']),
                                 sp_JSON['lang'])
            pos_list = data_JSON['pos']
            pos = []
            for p in pos_list: # turn this back into a TUPLE
                pos.append((p[0], p[1]))

            post_nom = []
            pre_nom = []
            for p in data_JSON['postnominal']:
                tempN = p['noun']
                tempA = p['adjectives']
                post_nom.append((tempN, tempA))
            for p in data_JSON['prenominal']:
                tempN = p['noun']
                tempA = p['adjectives']
                pre_nom.append((tempN, tempA))

            st = sentence.Sentence(sp, data_JSON['sentence'], pos, post_nom, pre_nom, False)
            temp_file = file_data(d['file'], st)
            sentences.append(temp_file)

    return sentences

def merge_JSON(data, file):
    """
    Merges sentence / file data into an existing JSON file.

    :param data: List of file_data objects to be saved.
    :param file: File to merge the data into.
    :return: None
    """
    outData = []

    for d in data:
        jsonData = {
            "file":d.file,
            "data":d.sentence.data_out()
        }
        if d.sentence.has_pair:
            outData.append(jsonData)

    with open(file, "r+") as f:
        data = json.load(f)
        data.extend(outData)
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Name of the JSON file to load.")
    parser.add_argument("-v", "--verified", help="Tells the program that the file has been human-verified.",
                        action='store_true')
    parser.add_argument("-w", "--whitelist", type=str, help="Text list of known adjectives.")
    parser.add_argument("-b", "--blacklist", type=str, help="Text list of known erroneously tagged adjectives.")
    parser.add_argument("-o", "--output", type=str,
                        help="The directory to output data files to.", default=getcwd())
    parser.add_argument("-t", "--test", help="Test mode, output goes to console.", action='store_true')
    parser.add_argument("-c", "--count", help="Simply counts the number of sentences in a file.", action='store_true')
    parser.add_argument("-l", "--lem", help="Lemmatize the data to extract root words.", action='store_true')

    arg = parser.parse_args()

    # Validate that the user gave the program something to do.
    if arg.input is None:
        print("You must specify a JSON file to load, use '-h' for help.")
        return 1
    if not os.path.isfile(arg.input):
        print("File " + arg.input + " not found or is not a file.")
        return 1
    if not arg.count:
        if os.path.isfile(arg.output):
            print("File " + arg.output + " needs to be a directory to output data to.")
            return 1

    # Load JSON file.
    sentences = read_JSON(arg.input)

    if arg.count:
        print("There are " + str(len(sentences)) + " sentences in this file.")
        return 0

    if arg.lem:
        for s in sentences:
            s.sentence.lem()
        return 0

    # List of known correctly tagged adjectives.
    if arg.whitelist is None:
        arg.whitelist = arg.output + '/whitelist.txt'
    adjective_whitelist = read_text(arg.whitelist)
    # List of known erroneously tagged adjectives.
    if arg.blacklist is None:
        arg.blacklist = arg.output + '/blacklist.txt'
    adjective_blacklist = read_text(arg.blacklist)

    # Use human-verified data to build a whitelist and blacklist for review.
    if arg.verified:
        potential_whitelist = [] # List of possible correctly tagged adjectives.
        potential_blacklist = [] # List of possible badly tagged adjectives.

        for st in sentences:
            temp_blacklist = st.sentence.find_bad()
            if len(temp_blacklist) > 0:
                potential_blacklist.extend(temp_blacklist)
            temp_whitelist = st.sentence.find_adjectives()
            if len(temp_whitelist) > 0:
                potential_whitelist.extend(temp_whitelist)

        for word in potential_whitelist:
            if not word in potential_blacklist:
                adjective_whitelist.append(word.lower())
        for word in potential_blacklist:
            if not word in potential_whitelist:
                adjective_blacklist.append(word.lower())

        adjective_whitelist = list(set(adjective_whitelist))
        adjective_whitelist.sort()
        adjective_blacklist = list(set(adjective_blacklist))
        adjective_blacklist.sort()
        save_text(adjective_whitelist, arg.whitelist)
        save_text(adjective_blacklist, arg.blacklist)

        if os.path.isfile(arg.output + '/verified-groups.json'):
            merge_JSON(sentences, arg.output + '/verified-groups.json')
        else:
            save_JSON(sentences, arg.output + '/verified-groups.json')
    # Use generated whitelist and blacklist data to generate a new JSON file for review.
    else:
        verified = []
        to_verify = []
        for st in sentences:
            st.sentence.filter(adjective_whitelist, adjective_blacklist)
            st.sentence.find_words()
            if st.sentence.review:
                to_verify.append(st)
            else:
                verified.append(st)

        print("Sentences left to verify:    " + str(len(to_verify)) + ".")
        print("Sentences added as verified: " + str(len(verified)) + ".")

        save_JSON(to_verify, arg.output + '/unverified-groups.json')

        if os.path.isfile(arg.output + '/verified-groups.json'):
            merge_JSON(verified, arg.output + '/verified-groups.json')
        else:
            save_JSON(verified, arg.output + '/verified-groups.json')

main()