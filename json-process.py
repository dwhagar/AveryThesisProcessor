#!/usr/bin/env python3
# A processor to read JSON data for Avery's corpus.
import argparse
import os.path
from os import walk, getcwd, makedirs
import json

# Import custom classes.
import speaker
import sentence

class fileData:
    def __init__(self, file, s):
        """
        Stores the sentence and the file name the sentence came from.

        :param file: Name of the original file.
        :param s: Sentence object to be stored.
        """
        self.file = file
        self.sentence = s

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Name of the JSON file to load.")
    parser.add_argument("-o", "--output", type=str, help="The directory to output data files to.",
                        default=getcwd())
    parser.add_argument("-t", "--test", help="Test mode, output goes to console.", action='store_true')

    arg = parser.parse_args()

    # Validate that the user gave the program something to do.
    if arg.input is None:
        print("You must specify a JSON file to load, use '-h' for help.")
        return 1
    if not os.path.isfile(arg.input):
        print("File " + arg.input + " not found or is not a file.")
        return 1
    if os.path.isfile(arg.output):
        print("File " + arg.output + " needs to be a directory.")
        return 1

    # Load JSON file.
    with open('data.txt') as json_file:
        data = json.load(json_file)

    sentences = [] # List of all the sentences by file.
    adj_blacklist = [] # List of blacklisted adjectives.
    for d in data:
        data_JSON = d['data']
        sp_JSON = data_JSON['speaker']
        st_JSON = data_JSON['sentence']
        sp = speaker.Speaker(sp_JSON['sid'],
                             sp_JSON['role'],
                             sp_JSON['name'],
                             sp_JSON['sex'],
                             float(sp_JSON['age']),
                             sp_JSON['lang'])
        pos_list = data_JSON['pos']
        pos = []
        for p in pos_list: # turn this back into a TUPLE
            pos.append((pos_list[0], pos_list[1]))

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

        st = sentence.Sentence(sp, st_JSON['sentence'], pos, post_nom, pre_nom, False)
        temp_file = fileData(d['file'], st)

main()