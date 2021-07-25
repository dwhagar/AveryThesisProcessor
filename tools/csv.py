# Tools for generating and writing CSV (Comma Separated Value) files.

def gen_stat_CSV(hdr, data):
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

def gen_standard_count_CSV(hdr, data):
    """
    Takes a dictionary of adjective counts and generates a CSV formatted list of strings ready for output to a file.

    :param hdr: A CSV Header
    :param data: A dictionary of adjective counts in the format of {'adjective':(prenominal, postnominal)}
    :return: A list of strings in the format of "adjective, prenom count, postnom count"
    """
    result = [hdr]

    for key in data.keys():
        line = key + "," + str(data[key][0]) + "," + str(data[key][1])
        result.append(line)

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

def noun_adj_matrix_gen_csv(matrix, adjs, nouns):
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