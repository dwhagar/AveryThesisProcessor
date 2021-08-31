#!/usr/bin/env python3

"""
This script will count all the adjectives in the adult and child data and create a CSV with all
of the counts of all of the adjectives.
"""

from os import getcwd
import os.path
import argparse
import tools

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--child", type=str, help="The JSON file to load child data from.")
    parser.add_argument("-a", "--adult", type=str, help="Directory of where to find adult data.")
    parser.add_argument("-o", "--output", type=str,
                        help="The directory to output CSV files to.", default=getcwd())

    arg = parser.parse_args()

    # Basic sanity checking.
    if arg.child is None:
        print("You need to specify a JSON file to laod.")
        return 1
    if arg.adult is None:
        print("You need to specify where the adult data should get loaded from.")
        return 1
    if not(os.path.isfile(arg.child)):
        print("Your child data file does not exist.")
        return 1
    if not(os.path.isdir(arg.adult)):
        print("Your adult data directory does not exist.")
        return 1
    if not(os.path.isdir(arg.output)):
        print("Your output path for the CSV file does not exist.")
        return 1

    # Load the child data.
    data = tools.read_JSON(arg.child)
    child_sentence_list = []
    for item in data:
        if item.sentence.has_pair and item.sentence.speaker.age.decimal < 8:
            child_sentence_list.append(item.sentence)

    # Load the adult data.
    files = tools.find_orfeo_files(arg.input)
    adult_sentence_list = []

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

        adult_sentence_list.extend(filtered_sentences)

    # Get a list of every adjective used anywhere.
    complete_adjective_list = []
    for this_sentence in child_sentence_list:
        complete_adjective_list.extend(this_sentence.find_adjectives())
    for this_sentence in adult_sentence_list:
        complete_adjective_list.extend(this_sentence.find_adjectives())

    child_counts = tools.count_from_list(child_sentence_list, complete_adjective_list)
    adult_counts = tools.count_from_list(adult_sentence_list, complete_adjective_list)

    # Now lets generate the CSV file.
    csv_header = "adjective, child prenominal count, child postnominal count, adult prenominal count, adult postnominal count"
    csv_data = tools.gen_complete_adjective_CSV(csv_header, complete_adjective_list, child_counts, adult_counts)
    tools.write_CSV(csv_data, os.path.join(arg.output, 'all-counts.csv'))

main()
