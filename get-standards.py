#!/usr/bin/env python3

"""
This script will process corpus data from the Oral CEFC database to determine the standard frequency
of prenominal and postnominal adjectives.
"""

from os import getcwd
import os.path
import argparse
import tools

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Directory to find corpus data.")
    parser.add_argument("-o", "--output", type=str,
                        help="The directory to output data files to.", default=getcwd())

    arg = parser.parse_args()

    # Basic sanity checking.
    if arg.input is None:
        print("You need to specify where to look for corups data, see -h for help.")
        return 1
    if not(os.path.isdir(arg.input)):
        print("Your input path does not exist.")
        return 1

    # Gather a life of all files to be loaded within the target directory.
    files = tools.find_orfeo_files(arg.input)

    sentences = []

    # Lets go through the files and
    for file in files:
        orfeo_file = file
        xml_file = file[0:-6] + ".xml"
        speaker_data = tools.read_speaker(xml_file)
        sentence_data = tools.read_sentences(orfeo_file, speaker_data)
        for sentence in sentence_data:
            if sentence.has_pair:
                print("FOUND ONE!")

main()