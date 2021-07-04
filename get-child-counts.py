#!/usr/bin/env python3

"""
This script will generate a list of adjective counts from a predefined list of adjectives.
"""

from os import getcwd
import os.path
import argparse
import tools

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="The JSON file to load data from.")
    parser.add_argument("-a", "--adjectives", type=str, help="The list of adjectives to count.")
    parser.add_argument("-o", "--output", type=str,
                        help="The directory to output data files to.", default=getcwd())

    arg = parser.parse_args()

    # Basic sanity checking.
    if arg.input is None:
        print("You need to specify a JSON file to laod.")
        return 1
    if arg.adjectives is None:
        print("You need to specify where to find the adjective list.")
        return 1
    if not(os.path.isfile(arg.input)):
        print("Your input file does not exist.")
        return 1
    if not(os.path.isfile(arg.adjectives)):
        print("Your adjective list does not exist.")
        return 1
    if not(os.path.isdir(arg.output)):
        print("Your output path does not exist.")
        return 1

    data = tools.read_JSON(arg.input)
    adjectives = tools.read_text(arg.adjectives)

    sentence_list = []

    # The count function will expect a list of sentences that does not include file
    # data.
    for item in data:
        if item.sentence.has_pair and item.sentence.speaker.age.decimal < 8:
            sentence_list.append(item.sentence)

    counts = tools.count_from_list(sentence_list, adjectives)

    # Now lets generate the CSV file.
    csv_header = "adjective, prenominal count, postnominal count"
    csv_data = tools.gen_standard_count_CSV(csv_header, counts)
    tools.write_CSV(csv_data, os.path.join(arg.output, 'children.csv'))

main()
