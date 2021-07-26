#!/usr/bin/env python3
# A processor to read XML data for Avery's corpus.

import argparse
import os.path
from os import getcwd, makedirs

# Import custom classes.
from tools.json import output_JSON
from tools.xml import find_XML, process_XML

def ageKey(val):
    """Simple function to allow sorting by the age of a speaker."""
    return val.age.decimal

def main():
    # Argument parsing.
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="The name of the XML file to be processed.")
    parser.add_argument("-d", "--dir", type=str, help="The directory name to find XML files to processed.")
    parser.add_argument("-o", "--output", type=str, help="The directory to output data files to.",
                        default=getcwd())
    parser.add_argument("-r", "--recursive", help="Should a directory be looked at recursively.", action='store_true')
    parser.add_argument("-t", "--test", help="Test mode, output goes to console.", action='store_true')

    arg = parser.parse_args()

    # Validate that the user gave the program something to do.
    if arg.file is None and arg.dir is None:
        print("You must specify either a file or directory to process, use '-h' for help.")
        return 1

    # Initialize a place to put the file list to process.
    file_list = []

    # Process any file and directory names and make a list to iterate through.
    if not arg.file is None:
        if not os.path.isfile(arg.file):
            print("File " + arg.file + " not found or is not a file.")
            return 1
        file_list.append(arg.file)
    elif not arg.dir is None:
        if not os.path.isdir(arg.dir):
            print("Directory " + arg.dir + " not found or is not a directory.")
            return 1
        file_list = find_XML(arg.dir, arg.recursive)

    # Process all the XML files in the list.
    data = [] # Master list of all data as a list of FD objects.

    for file in file_list:
        print("Processing file '" + file + "'...")
        file_data = process_XML(file)
        data.extend(file_data)

    # These lists are for output to JSON files.
    out_data = [] # Master list formatted as dictionary.
    pairs_only = [] # List of only those FD objects that have noun/adjective groups.

    # Build our data for output to JSON format.
    for d in data:
        this_JSON = d.data_out()
        out_data.append(this_JSON)
        if d.sentence.has_pair:
            pairs_only.append(this_JSON)

    print("Processing complete.")
    if not arg.test:
        makedirs(arg.output, exist_ok=True)

    print("Outputting only sentence data with noun/adjective pairs to unverified-groups.json...")
    output_JSON(pairs_only, os.path.join(arg.output, 'unverified-groups.json'), arg.test)
    print("Outputting complete data set to complete.json...")
    output_JSON(out_data, os.path.join(arg.output, 'complete.json'), arg.test)

    return 0

main()