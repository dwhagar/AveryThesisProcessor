#!/usr/bin/env python3
# A processor to read XML data for Avery's corpus.

import argparse
import os.path
from os import getcwd, makedirs
import xml.etree.ElementTree as ET

# Import custom classes.
from tools.json_tools import output_JSON
from tools.xml_tools import get_attribute, find_XML, corpus_PB12, corpus_271

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
    data = [] # Master list of all data processed.
    out_data = [] # Data for output to JSON.
    pairs_only = [] # Only sentences which have adjective / noun groups.
    for file in file_list:
        print("Processing file '" + file + "'...")

        corpusTree = ET.parse(file)
        corpusRoot = corpusTree.getroot()

        # Need to determine file version for processing, since different files have
        # different capitalization, we need to account for that.
        ver = get_attribute(corpusRoot, 'version')
        if ver is None:
            ver = get_attribute(corpusRoot, 'Version')

        lst = []

        # Now branch to the proper processor.
        if ver == 'PB1.2':
            lst = corpus_PB12(corpusRoot)
            data.extend(lst)
        elif ver == '2.7.1':
            lst = corpus_271(corpusRoot)
            data.extend(lst)

        for d in lst:
            json_data = {
                "file":file,
                "data":d.data_out()
            }
            out_data.append(json_data)
            if d.has_pair:
                pairs_only.append(json_data)

    for d in data:
        out_data.append(d.data_out())

    print("Processing complete.")
    if not arg.test:
        makedirs(arg.output, exist_ok=True)

    print("Outputting only sentence data with noun/adjective pairs to unverified-groups.json...")
    output_JSON(pairs_only, os.path.join(arg.output, 'json-data/unverified-groups.json'), arg.test)
    print("Outputting complete data set to complete.json...")
    output_JSON(out_data, os.path.join(arg.output, 'complete.json'), arg.test)

    return 0

main()