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
    if not(os.path.isdir(arg.output)):
        print("Your output path does not exist.")
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

        # Now we need to throw away any sentence that does not have a
        # noun adjective group in it.
        filtered_sentences = []

        for sentence in sentence_data:
            if sentence.has_pair:
                filtered_sentences.append(sentence)

        sentences.extend(filtered_sentences)

    # Now we need to do some counting.
    adjective_list = tools.text.read_text(os.path.join(arg.input, 'data/adjective-list.txt'))

    # Going to store the data in a dictionary of tuples.  Each adjective will
    # have an entry and that entry will have a tuple of (pre, post) for that
    # adjective.
    counts = tools.count_from_list(sentences, adjective_list)

    # Now lets generate the CSV file.
    csv_header = "adjective, prenominal count, postnominal count"
    csv_data = tools.gen_standard_count_CSV(csv_header, counts)
    tools.write_CSV(csv_data, os.path.join(arg.output, 'standards.csv'))

main()