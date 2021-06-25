# Standard tools for working with Thesis data.

import json
import os.path

# Custom packages
import sentence
import speaker
from .file_data import file_data

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

def count_noun_adj_helper(groups, adjectives, matrix):
    """
    Uses a given 2-dimensional dictionary matrix and list of adjectives / nouns to produce a count.

    :param groups:  A list of noun/adjective groups in the format of:
    [(noun, [(adjective, adjective-lemma), ...], noun-lemma), ...]
    :param adjectives: All adjective lemmas that need to be checked.
    :param matrix: A 2-dimensional dictionary matrix.
    :return: The matrix with counts filled in.
    """
    for adj in adjectives:
        for g in groups:
            n = g[2]
            for a in g[1]:
                if a[1] == adj:
                    matrix[adj.lower()][n.lower()] += 1

    return matrix

def count_noun_adj(sentences, adjectives, nouns, all_older, all_younger, prenom_older, postnom_older, prenom_younger, postnom_younger):
    """
    Goes through a list of sentence objects with a list of adjectives and counts how
    often each adjective is paired with a particular noun.

    :param sentences: A list of sentence objects.
    :param adjectives: A list of adjective lemmas.
    :param nouns: A list of noun lemmas.
    :param all_older: All adjectives used by those classified as older.
    :param all_younger: All adjectives used by those classified as younger.
    :param prenom_older: All prenominal adjectives used by older speakers.
    :param postnom_older: All postnominal adjectives used by older speakers.
    :param prenom_younger: All prenominal adjectives used by younger speakers.
    :param postnom_younger: All postnominal adjective used by younger speakers.
    :return: 2-dimensional dictionaries for all input categories.
    """
    # Define the 2 dimensional dictionary to store all the associated numbers.
    matrix = {} # This will be a master list of all occurances.
    for a in adjectives:
        matrix[a.lower()] = {}
        for n in nouns:
            matrix[a.lower()][n.lower()] = 0

    older_matrix = matrix.copy() # For only older speakers.
    younger_matrix = matrix.copy() # For only younger speakers.
    older_pre_matrix = matrix.copy() # Older / Prenominal Groups
    older_post_matrix = matrix.copy() # Older / Postnominal Groups
    younger_pre_matrix = matrix.copy() # Younger / Prenominal Groups
    younger_post_matrix = matrix.copy() # Younger / Postnominal Groups

    # First we will gather all of the lists of groups.
    all_groups = []
    older_groups = []
    younger_groups = []
    older_pre_groups = []
    older_post_groups = []
    younger_pre_groups = []
    younger_post_groups = []

    for s in sentences:
        all_groups.extend(s.sentence.pre_nom)
        all_groups.extend(s.sentence.post_nom)
        if s.sentence.speaker.age.decimal >= 8:
            older_groups.extend(s.sentence.pre_nom)
            older_groups.extend(s.sentence.post_nom)
            older_pre_groups.extend(s.sentence.pre_nom)
            older_post_groups.extend(s.sentence.post_nom)
        else:
            younger_groups.extend(s.sentence.pre_nom)
            younger_groups.extend(s.sentence.post_nom)
            younger_pre_groups.extend(s.sentence.pre_nom)
            younger_post_groups.extend(s.sentence.post_nom)

    # Now that all the prep work is done we have to actually perform the counting.
    matrix = count_noun_adj_helper(all_groups, adjectives, matrix)
    older_matrix = count_noun_adj_helper(older_groups, all_older, older_matrix)
    older_pre_matrix = count_noun_adj_helper(older_pre_groups, prenom_older, older_pre_matrix)
    older_post_matrix = count_noun_adj_helper(older_post_groups, postnom_older, older_post_matrix)
    younger_matrix = count_noun_adj_helper(younger_groups, all_younger, younger_matrix)
    younger_pre_matrix = count_noun_adj_helper(younger_pre_groups, prenom_younger, younger_pre_matrix)
    younger_post_matrix = count_noun_adj_helper(younger_post_groups, postnom_younger, younger_post_matrix)

    return matrix,\
           older_matrix,\
           younger_matrix,\
           older_pre_matrix,\
           older_post_matrix,\
           younger_pre_matrix,\
           younger_post_matrix

def matrix_gen_csv(matrix, adjs, nouns):
    """
    Takes a matrix of adjective/noun pair counts and converts it into CSV compatible data.

    :param matrix: The 2-dimensional matrix of adjective/noun pair counts.
    :param adjs: A list of possible adjectives.
    :param nouns: A list of possible nouns.
    :return: A list of strings compatible for CSV output and the header.
    """
    adjs.sort()
    nouns.sort()

    data = []

    for a in adjs:
        line = [a]
        for n in nouns:
            line.append(matrix[a.lower()][n.lower()])

        data.append(line)

    return data