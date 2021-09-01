#!/usr/bin/env python3

"""
This script will count all the adjectives in the adult and child data and create a CSV with all
of the counts of all of the adjectives.
"""

from os import getcwd
import os.path
import argparse
import tools

def sentence_filter_helper(data):
    """Filters a list of sentence objects by if they have adjectives / noun groups."""
    result = []
    for this_sentence in data:
        if this_sentence.has_pair:
            result.append(this_sentence)

    return result

def adj_list_helper(data):
    """Generates a list of adjective lemmas from a list of sentences."""
    result =  []
    for this_sentence in data:
        adjectives,lemmas = this_sentence.find_adjectives()
        result.extend(lemmas)

    return result

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
        if item.sentence.speaker.age.decimal < 8:
            child_sentence_list.append(item.sentence)

    # Load the adult data.
    files = tools.find_orfeo_files(arg.adult)
    adult_sentence_list = []

    # Lets go through the files and
    for file in files:
        orfeo_file = file
        xml_file = file[0:-6] + ".xml"
        speaker_data = tools.read_speaker(xml_file)
        sentence_data = tools.read_sentences(orfeo_file, speaker_data)
        adult_sentence_list.extend(sentence_data)

    # Filter all sentences by if they have pairs or not.
    adult_sentence_list = sentence_filter_helper(adult_sentence_list)
    child_sentence_list = sentence_filter_helper(child_sentence_list)

    # Get a list of every adjective used anywhere.
    complete_adjective_list = []
    complete_adjective_list.extend(adj_list_helper(child_sentence_list))
    complete_adjective_list.extend(adj_list_helper(adult_sentence_list))

    complete_adjective_list = list(set(complete_adjective_list))

    print("There are " + str(len(complete_adjective_list)) + " adjectives.")

    print("Counting adjective usage in child data.")
    child_counts = tools.count_from_list(child_sentence_list, complete_adjective_list)
    print("Counting adjective usage in adult data.")
    adult_counts = tools.count_from_list(adult_sentence_list, complete_adjective_list)

    # Now lets generate the CSV file.
    csv_header = "adjective, child prenominal count, child postnominal count, adult prenominal count, adult postnominal count"
    csv_data = tools.gen_complete_adjective_CSV(csv_header, complete_adjective_list, child_counts, adult_counts)
    tools.write_CSV(csv_data, os.path.join(arg.output, 'all-counts.csv'))

main()
