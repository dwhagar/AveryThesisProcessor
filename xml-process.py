# A processor to read XML data for Avery's corpus.

import argparse
import os.path
import xml.etree.ElementTree as ET

import speakerData

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="The name of the XML file to be processed.", required=True)
    arg = parser.parse_args()

    if not os.path.isfile(arg.file):
        print("File" + arg.file + "not found.")
        return 1

    corpusXML = ET.parse(arg.file)



    return 0

main()