#!/usr/bin/env python3

"""
This script will process corpus data from the Oral CEFC database to determine the standard frequency
of prenominal and postnominal adjectives.
"""

from os import getcwd
import os.path
import argparse
import tools

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Directory to find corpus data.")
    parser.add_argument("-o", "--output", type=str,
                        help="The directory to output data files to.", default=getcwd())

    arg = parser.parse_args()

    # Basic sanity checking.
    if arg.input is None:
        print("You need to specify where to look for corups data, see -h for help.")
        return 1
    if not(os.path.isdir(arg.input)):
        print("Your input path does not exist.")
        return 1

    # Gather a life of all files to be loaded within the target directory.
    files = tools.find_orfeo_files(arg.input)

    sentences = []

    # Lets go through the files and
    for file in files:
        orfeo_file = file
        xml_file = file[0:-6] + ".xml"
        speaker_data = tools.read_speaker(xml_file)
        sentence_data = tools.read_sentences(orfeo_file, speaker_data)

        # Now we need to throw away any sentence that does not have a
        # noun adjective group in it.
        filtered_sentences = []

        for sentence in sentence_data:
            if sentence.has_pair:
                filtered_sentences.append(sentence)

        sentences.extend(filtered_sentences)

    # Now we need to do some counting.
    adjective_list = ['petit', 'grand', 'autre', 'gros', 'beau', 'gentil',
                      'même', 'cassé', 'bon', 'vrai', 'méchant', 'haut',
                      'dur', 'bas', 'vilain', 'dernier', 'rouge', 'jaune',
                      'pareil', 'chaud', 'caché', 'coquin', 'ferme', 'premier',
                      'froid', 'vert', 'seul', 'nul', 'ouvert', 'deuxième',
                      'joli', 'mauvais', 'préféré', 'lourd', 'court', 'sûr',
                      'double', 'prochain', 'nouveau', 'énorme', 'long', 'prêt',
                      'vieux', 'deux', 'las', 'minuscule', 'mécanique',
                      'malheureux', 'pompier', 'doux', 'para', 'animé',
                      'en_bas', 'bleu', 'noir', 'rose', 'sale', 'magique',
                      'blanc', 'orange', 'châtain', 'râpé', 'violet', 'carré',
                      'gris', 'clair', 'foncé', 'collant', 'roux', 'clefs',
                      'rond', 'sombre', 'gauche', 'brun', 'propre', 'fermé',
                      'gras', 'sage', 'mouillé', 'triste', 'rigolo', 'entier',
                      'adulte', 'bête', 'malade', 'collé', 'arrière', 'chéri',
                      'fort', 'plouf', 'transporteurs', 'dodu', 'pointu',
                      'couteau', 'brillant']

    # Going to store the data in a dictionary of tuples.  Each adjective will
    # have an entry and that entry will have a tuple of (pre, post) for that
    # adjective.
    counts = {}

    # Go through each adjective and all the sentences looking for said adjective.
    for adjective in adjective_list:
        # Initialize counter variables.
        pre_count = 0
        post_count = 0

        # Count the adjectives found in each position for each sentence.
        for sentence in sentences:
            this_pre_count, this_post_count = sentence.get_adjective_count(adjective)
            pre_count += this_pre_count
            post_count += this_post_count

        counts[adjective] = (pre_count, post_count)

    csv_header = "adjective, prenominal count, postnominal count"

    csv_data = tools.gen_standard_count_CSV(csv_header, counts)


main()