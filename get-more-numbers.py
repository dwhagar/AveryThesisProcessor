#!/usr/bin/env python3

"""
This script will count all the adjectives in the adult and child data and create a CSV with all
of the counts of all of the adjectives.
"""

from os import getcwd
import os.path
import argparse
import tools

def count_words(data):
    """
    Counts the words in every sentence in a list of sentences.

    :param data: A list of Sentence objects
    :return: An integer of # of words counted
    """
    result = 0

    for item in data:
        result = result + item.count_words()

    return result

def adj_adult_age_counts(data, adjs):
    """
    Obtains adjective counts for adult data.

    :param data: List of Sentence objects
    :param adjs: A list of adjectives to count occurrences of
    :return: An integer of the number of adjectives for this age
    """
    result = 0

    for item in data:
        if item.has_pair:
            for word in adjs:
                this_pre_count, this_post_count = item.get_adjective_count(word)
                result += this_pre_count + this_post_count

    return result

def adj_child_age_counts(data, age_low, age_high, adjs):
    """
    Obtains adjective counts for each age bin of 6 months.

    :param data: List of Sentence objects
    :param age_low: The lower limit on ages in months
    :param age_high: The upper limit on ages in months
    :param adjs: A list of adjectives to count occurrences of
    :return: An integer of the number of adjectives for this age
    """
    result = 0

    for item in data:
        speaker_age = item.speaker.age.decimal * 12
        if item.has_pair:
            for word in adjs:
                if age_high < 48:
                    if age_low <= speaker_age < age_high:
                        this_pre_count, this_post_count = item.get_adjective_count(word)
                        result += this_pre_count + this_post_count
                else:
                    if age_low <= speaker_age <= 48:
                        this_pre_count, this_post_count = item.get_adjective_count(word)
                        result += this_pre_count + this_post_count

    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--child", type=str, help="The JSON file to load child data from.")
    parser.add_argument("-a", "--adult", type=str, help="Directory of where to find adult data.")
    parser.add_argument("-w", "--words", type=str, help="The list of adjectives to count.")
    parser.add_argument("-o", "--output", type=str, help="The directory to output CSV files to.", default=getcwd())

    arg = parser.parse_args()

    # Basic sanity checking.
    if arg.child is None:
        print("You need to specify a JSON file to load.")
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
    if not(os.path.isfile(arg.words)):
        print("Your adjective list does not exist.")
        return 1

    # Load the child data.
    data = tools.read_JSON(arg.child)
    adjectives = tools.read_text(arg.words)
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

    # Get word totals.
    child_words = count_words(child_sentence_list)
    adult_words = count_words(adult_sentence_list)
    print("The total words in the Child Data is:  " + str(child_words))
    print("The total words in the Adult Data is:  " + str(adult_words))

    # Age bins of 6 month increments
    print("Counting adjectives in child data for each bin.")
    for age_low in range(19, 48, 6):
        age_high = age_low + 6
        if age_high > 48:
            age_high = 48

        child_adjective_count = adj_child_age_counts(child_sentence_list, age_low, age_high, adjectives)
        print("From age " + str(age_low) + " to " + str(age_high) + ":  " + str(child_adjective_count) + ".")

    print("Counting adjectives in the adult data.")
    adult_adjective_count = adj_adult_age_counts(adult_sentence_list, adjectives)
    print("The adult data has:  " + str(adult_adjective_count) + ".")

main()
