#!/usr/bin/env python3
# A processor to read JSON data for Avery's corpus.
import argparse
import os.path
from os import getcwd
import json

# Import custom classes.
import speaker
import sentence

class file_data:
    def __init__(self, file, s):
        """
        Stores the sentence and the file name the sentence came from.

        :param file: Name of the original file.
        :param s: Sentence object to be stored.
        """
        self.file = file
        self.sentence = s

def save_text(data, file):
    """
    Writes the data to the file as a text file.

    :param data: List data to be saved.
    :param file: File to save data to.
    :return: None
    """
    for i in range(0, len(data)):
       data[i] = data[i] + '\n'

    f = open(file, 'w')
    f.writelines(data)
    f.close()

def read_text(file):
    """
    Reads text data from a file, one list item per line.

    :param file: File to read data from.
    :return: List of data items from the file.
    """
    result = []
    if os.path.isfile(file):
        f = open(file, 'r')
        data = f.readlines()
        f.close()

        for d in data:
            d = d.strip('\n')
            d = d.strip()
            result.append(d)

    return result

def save_JSON(data, file):
    """
    Saves sentence / file data to a JSON file.

    :param data: List of file_data objects to be saved
    :param file: File to save objects to
    :return: None
    """
    outData = []

    for d in data:
        jsonData = {
            "file":d.file,
            "data":d.sentence.data_out()
        }
        if d.sentence.has_pair:
            outData.append(jsonData)

    with open(file, 'w') as f:
        json.dump(outData, f, indent=4, ensure_ascii=False)

def read_JSON(file):
    """
    Reads data into memory from a JSON file.

    :param file: File to read from.
    :return: A list of file_data objects containing sentence data and original file names.
    """
    # Load JSON file.
    with open(file) as json_file:
        data = json.load(json_file)

    sentences = [] # List of all the sentences by file.
    for d in data:
        data_JSON = d['data']
        if not data_JSON['sentence'][:2] == "::":
            sp_JSON = data_JSON['speaker']
            sp = speaker.Speaker(sp_JSON['sid'],
                                 sp_JSON['role'],
                                 sp_JSON['name'],
                                 sp_JSON['sex'],
                                 float(sp_JSON['age']),
                                 sp_JSON['lang'])
            pos_list = data_JSON['pos']
            pos = []
            for p in pos_list: # turn this back into a TUPLE
                pos.append((p[0], p[1]))

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

            st = sentence.Sentence(sp, data_JSON['sentence'], pos, post_nom, pre_nom, False)
            temp_file = file_data(d['file'], st)
            sentences.append(temp_file)

    return sentences

def merge_JSON(data, file):
    """
    Merges sentence / file data into an existing JSON file.

    :param data: List of file_data objects to be saved.
    :param file: File to merge the data into.
    :return: None
    """
    outData = []

    for d in data:
        jsonData = {
            "file":d.file,
            "data":d.sentence.data_out()
        }
        if d.sentence.has_pair:
            outData.append(jsonData)

    with open(file, "r+") as f:
        data = json.load(f)
        data.extend(outData)
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)

def gen_CSV(hdr, data):
    """Generate a list of CSV formatted strings from a list of statistical data."""
    result = [hdr]

    # Add data to file.
    for item in data:
        dataLine = ""
        for element in item:
            if len(dataLine) == 0:
                if type(element) == str:
                    dataLine = element
                else:
                    dataLine = "=" + str(element)
            else:
                if type(element) == str:
                    dataLine += "," + element
                else:
                    dataLine += ",=" + str(element)
        result.append(dataLine)

    return result

def write_CSV(data, file, test = False):
    """Write CSV formatted data to a file."""
    if len(data) > 1:
        if test:
            for line in data:
                print(line)
        else:
            print("Saving CSV data to '" + file + "'.")
            f = open(file, "w")

            for line in data:
                print(line, file=f)

            f.close()
    else:
        print("No data found for '" + file + "', skipping.")

def count_adj(master_list, all_older, all_younger, prenom_older, postnom_older, prenom_younger, postnom_younger):
    """
    Given a master adjective list it will generate a count of all adjectives used
    in the various positions (older, younger, prenominal, postnominal).

    :param master_list: A master list of all adjectives used.
    :param all_older: All adjectives used by those classified as older.
    :param all_younger: All adjectives used by those classified as younger.
    :param prenom_older: All prenominal adjectives used by older speakers.
    :param postnom_older: All postnominal adjectives used by older speakers.
    :param prenom_younger: All prenominal adjectives used by younger speakers.
    :param postnom_younger: All postnominal adjective used by younger speakers.
    :return: Output is a tuple with the format of:
    (lemma, all, older, younger, prenom-older, postnom-older, prenom-younger, postnom-younger)
    """
    canonical = list(set(master_list)) # Canonical list of all adjectives used.
    counts = []

    for adj in canonical:
        adj_count_all = master_list.count(adj)
        adj_count_older = all_older.count(adj)
        adj_count_younger = all_younger.count(adj)
        adj_count_pre_older = prenom_older.count(adj)
        adj_count_post_older = postnom_older.count(adj)
        adj_count_pre_younger = prenom_younger.count(adj)
        adj_count_post_younger = postnom_younger.count(adj)
        adj_counts = (
            adj,
            adj_count_all,
            adj_count_older,
            adj_count_younger,
            adj_count_pre_older,
            adj_count_post_older,
            adj_count_pre_younger,
            adj_count_post_younger
        )
        counts.append(adj_counts)

    return counts

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Name of the JSON file to load.")
    parser.add_argument("-v", "--verified", help="Tells the program that the file has been human-verified.",
                        action='store_true')
    parser.add_argument("-w", "--whitelist", type=str, help="Text list of known adjectives.")
    parser.add_argument("-b", "--blacklist", type=str, help="Text list of known erroneously tagged adjectives.")
    parser.add_argument("-o", "--output", type=str,
                        help="The directory to output data files to.", default=getcwd())
    parser.add_argument("-t", "--test", help="Test mode, output goes to console.", action='store_true')
    parser.add_argument("-c", "--count", help="Simply counts the number of sentences in a file.", action='store_true')
    parser.add_argument("-l", "--lem", help="Lemmatize the data to extract root words.", action='store_true')
    parser.add_argument("-a", "--age", help="Generates age-specific lists of adjectives.", action='store_true')
    parser.add_argument("-l", "--colors", help="Processes all the colors and positions for each age group.", action='store_true')

    arg = parser.parse_args()

    # Validate that the user gave the program something to do.
    if arg.input is None:
        print("You must specify a JSON file to load, use '-h' for help.")
        return 1
    if not os.path.isfile(arg.input):
        print("File " + arg.input + " not found or is not a file.")
        return 1
    if not arg.count:
        if os.path.isfile(arg.output):
            print("File " + arg.output + " needs to be a directory to output data to.")
            return 1

    # Load JSON file.
    sentences = read_JSON(arg.input)

    if arg.count:
        print("There are " + str(len(sentences)) + " sentences in this file.")
        return 0

    # Lemmatize the data and generate master adjective lists for all ages.
    if arg.lem:
        for s in sentences:
            s.sentence.lem()

        save_JSON(sentences, arg.output + '/lem-data.json')
        return 0

    # Generate the adjective lists based on the age of 8.
    if arg.age:
        all_lemma = []
        older_lemma = []
        younger_lemma = []
        older_pre_lemma = []
        older_post_lemma = []
        younger_pre_lemma = []
        younger_post_lemma = []

        for s in sentences:
            s.sentence.lem()
            # Note the use of the 'not_needed' variable, this is a placeholder since
            # the function returns both adjectives and lemmas.  We aren't worried about
            # the inflected adjectives, so we can throw it away.
            if s.sentence.speaker.age.decimal >= 8:
                not_needed, temp_lemma = s.sentence.find_adjectives()
                all_lemma.extend(temp_lemma)
                older_lemma.extend(temp_lemma)
                temp_pre, temp_post = s.sentence.get_pre_post_lists()
                older_pre_lemma.extend(temp_pre)
                older_post_lemma.extend(temp_post)
            else:
                not_needed, temp_lemma = s.sentence.find_adjectives()
                all_lemma.extend(temp_lemma)
                younger_lemma.extend(temp_lemma)
                temp_pre, temp_post = s.sentence.get_pre_post_lists()
                younger_pre_lemma.extend(temp_pre)
                younger_post_lemma.extend(temp_post)

        # Now we need to count everything up.
        counts = count_adj(
            all_lemma,
            older_lemma,
            younger_lemma,
            older_pre_lemma,
            older_post_lemma,
            younger_pre_lemma,
            younger_post_lemma
        )

        # Now lets output the data out.
        header = "Lemma, Full Count, Older, Younger, Older Prenominal, Older Postnominal, Younger Prenominal, Older Postnominal"
        counts_csv = gen_CSV(header, counts)
        counts_file = arg.output + "/counts.csv"
        write_CSV(counts_csv, counts_file)

        return 0

    # Generate color adjectives only in each position.
    if arg.colors:
        all_colors = []
        older_colors = []
        younger_colors = []
        older_pre_colors = []
        older_post_colors = []
        younger_pre_colors = []
        younger_post_colors = []

        for s in sentences:
            s.sentence.lem()
            # Note the use of the 'not_needed' variable, this is a placeholder since
            # the function returns both adjectives and lemmas.  We aren't worried about
            # the inflected adjectives, so we can throw it away.
            if s.sentence.speaker.age.decimal >= 8:
                temp_older_pre_colors, temp_older_post_colors = s.sentence.get_colors()
                older_pre_colors.extend(temp_older_pre_colors)
                older_post_colors.extend(temp_older_post_colors)
            else:
                temp_younger_pre_colors, temp_younger_post_colors = s.sentence.get_colors()
                younger_pre_colors.extend(temp_younger_pre_colors)
                younger_post_colors.extend(temp_younger_post_colors)

        # Get the list and ready to count for every single color adjective.
        all_colors.extend(older_pre_colors)
        all_colors.extend(older_post_colors)
        all_colors.extend(younger_pre_colors)
        all_colors.extend(younger_post_colors)

        # For completeness produce a list of all colors used in each age group.
        older_colors.extend(older_pre_colors)
        older_colors.extend(older_post_colors)
        younger_colors.extend(younger_pre_colors)
        younger_colors.extend(younger_post_colors)

        # Now we need to count everything up.
        counts = count_adj(
            all_colors,
            older_colors,
            younger_colors,
            older_pre_colors,
            older_post_colors,
            younger_pre_colors,
            younger_post_colors
        )

        # Now lets output the data out.
        header = "Lemma, Full Count, Older, Younger, Older Prenominal, Older Postnominal, Younger Prenominal, Older Postnominal"
        counts_csv = gen_CSV(header, counts)
        counts_file = arg.output + "/colors.csv"
        write_CSV(counts_csv, counts_file)

        return 0

    # List of known correctly tagged adjectives.
    if arg.whitelist is None:
        arg.whitelist = arg.output + '/whitelist.txt'
    adjective_whitelist = read_text(arg.whitelist)
    # List of known erroneously tagged adjectives.
    if arg.blacklist is None:
        arg.blacklist = arg.output + '/blacklist.txt'
    adjective_blacklist = read_text(arg.blacklist)

    # Use human-verified data to build a whitelist and blacklist for review.
    if arg.verified:
        potential_whitelist = [] # List of possible correctly tagged adjectives.
        potential_blacklist = [] # List of possible badly tagged adjectives.

        for st in sentences:
            temp_blacklist = st.sentence.find_bad()
            if len(temp_blacklist) > 0:
                potential_blacklist.extend(temp_blacklist)
            temp_whitelist = st.sentence.find_adjectives()
            if len(temp_whitelist) > 0:
                potential_whitelist.extend(temp_whitelist)

        for word in potential_whitelist:
            if not word in potential_blacklist:
                adjective_whitelist.append(word.lower())
        for word in potential_blacklist:
            if not word in potential_whitelist:
                adjective_blacklist.append(word.lower())

        adjective_whitelist = list(set(adjective_whitelist))
        adjective_whitelist.sort()
        adjective_blacklist = list(set(adjective_blacklist))
        adjective_blacklist.sort()
        save_text(adjective_whitelist, arg.whitelist)
        save_text(adjective_blacklist, arg.blacklist)

        if os.path.isfile(arg.output + '/verified-groups.json'):
            merge_JSON(sentences, arg.output + '/verified-groups.json')
        else:
            save_JSON(sentences, arg.output + '/verified-groups.json')
    # Use generated whitelist and blacklist data to generate a new JSON file for review.
    else:
        verified = []
        to_verify = []
        for st in sentences:
            st.sentence.filter(adjective_whitelist, adjective_blacklist)
            st.sentence.sanitize_words()
            st.sentence.sanitize_sentence()
            st.sentence.find_words()
            if st.sentence.review:
                to_verify.append(st)
            else:
                verified.append(st)

        print("Sentences left to verify:    " + str(len(to_verify)) + ".")
        print("Sentences added as verified: " + str(len(verified)) + ".")

        save_JSON(to_verify, arg.output + '/unverified-groups.json')

        if os.path.isfile(arg.output + '/verified-groups.json'):
            merge_JSON(verified, arg.output + '/verified-groups.json')
        else:
            save_JSON(verified, arg.output + '/verified-groups.json')

main()