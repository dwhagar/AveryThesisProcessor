# Tools for dealing with coprus data converted into JSON format.

import json

# Custom packages
import sentence
import speaker
from .file_data import file_data

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