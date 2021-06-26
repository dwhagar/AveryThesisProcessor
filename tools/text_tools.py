# Tools for reading / writing text files.

import os.path

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