#!/usr/bin/env python3
# A processor to read JSON data for Avery's corpus.
import argparse
import os.path
from os import getcwd

# Import custom classes.
import tools

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
    parser.add_argument("-r", "--colors", help="Processes all the colors and positions for each age group.", action='store_true')
    parser.add_argument("-n", "--nouns", help="Counts noun/adjective occurrences fro each age group.", action='store_true')
    parser.add_argument("-p", "--repair", help="Reprocesses the input file to regroup adjective/noun pairs.", action='store_true')

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
    sentences = tools.read_JSON(arg.input)

    if arg.count:
        print("There are " + str(len(sentences)) + " sentences in this file.")
        return 0

    # Lemmatize the data and generate master adjective lists for all ages.
    if arg.lem:
        for s in sentences:
            s.sentence.lem()

        tools.save_JSON(sentences, arg.output + '/lem-data.json')
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
        counts = tools.count_adj(
            all_lemma,
            older_lemma,
            younger_lemma,
            older_pre_lemma,
            older_post_lemma,
            younger_pre_lemma,
            younger_post_lemma
        )

        # Now lets output the data out.
        header = "Lemma, Full Count, Older, Younger, Older Prenominal, Older Postnominal, Younger Prenominal, Younger Postnominal"
        counts_csv = tools.gen_CSV(header, counts)
        counts_file = arg.output + "/counts.csv"
        tools.write_CSV(counts_csv, counts_file)

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
        counts = tools.count_adj(
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
        counts_csv = tools.gen_CSV(header, counts)
        counts_file = arg.output + "/colors.csv"
        tools.write_CSV(counts_csv, counts_file)

        return 0

    # Reprocess the input file to generate new adjective/noun groups.
    if arg.repair:
        non_words_list = tools.read_text(arg.output + "/non-words.txt")
        for s in sentences:
            s.sentence.filter_all(non_words_list)

        tools.save_JSON(sentences, arg.output + "/repaired-data.json")

        return 0

    # Generate the counts of each adjective and noun combinations.
    if arg.nouns:
        # A place for all the adjectives to check.
        all_lemma = []
        older_lemma = []
        younger_lemma = []
        older_pre_lemma = []
        older_post_lemma = []
        younger_pre_lemma = []
        younger_post_lemma = []

        # A place for all the nouns to check.
        all_noun = []

        # Get a complete list of all nouns and adjectives.
        for s in sentences:
            s.sentence.lem()
            # Note the use of the 'not_needed' variable, this is a placeholder since
            # the function returns both adjectives and lemmas.  We aren't worried about
            # the inflected adjectives, so we can throw it away.
            not_needed, temp_lemma = s.sentence.find_adjectives()
            temp_pre_nouns, temp_post_nouns = s.sentence.get_nouns()
            all_lemma.extend(temp_lemma)
            temp_pre, temp_post = s.sentence.get_pre_post_lists()
            all_noun.extend(temp_pre_nouns)
            all_noun.extend(temp_post_nouns)

            if s.sentence.speaker.age.decimal >= 8:
                older_lemma.extend(temp_lemma)
                older_pre_lemma.extend(temp_pre)
                older_post_lemma.extend(temp_post)
            else:
                younger_lemma.extend(temp_lemma)
                younger_pre_lemma.extend(temp_pre)
                younger_post_lemma.extend(temp_post)

        # Get the adjective counts
        counts = tools.count_adj(
            all_lemma,
            older_lemma,
            younger_lemma,
            older_pre_lemma,
            older_post_lemma,
            younger_pre_lemma,
            younger_post_lemma
        )

        reduced_lemma = list(set(all_lemma))
        reduced_older = list(set(older_lemma))
        reduced_younger = list(set(younger_lemma))
        reduced_older_pre = list(set(older_pre_lemma))
        reduced_older_post = list(set(older_post_lemma))
        reduced_younger_pre = list(set(younger_pre_lemma))
        reduced_younger_post = list(set(younger_post_lemma))

        # Now we need to remove all adjectives from the lists that occur less
        # than 20 times.
        for c in counts:
            if c[1] < 20:
                if c[0] in reduced_lemma: reduced_lemma.remove(c[0])
                if c[0] in reduced_older: reduced_older.remove(c[0])
                if c[0] in reduced_younger: reduced_younger.remove(c[0])
                if c[0] in reduced_older_pre: reduced_older_pre.remove(c[0])
                if c[0] in reduced_older_post: reduced_older_post.remove(c[0])
                if c[0] in reduced_younger_pre: reduced_younger_pre.remove(c[0])
                if c[0] in reduced_younger_post: reduced_younger_post.remove(c[0])

        # Generate a reduced noun set.
        canon_nouns = list(set(all_noun))
        reduced_nouns = canon_nouns[:]
        noun_counts = []
        for n in canon_nouns:
            noun_counts.append((n, all_noun.count(n)))

        for nc in noun_counts:
            if nc[1] <= 4:
                reduced_nouns.remove(nc[0])

        # Count everything.
        matrix, older_matrix, younger_matrix, older_pre_matrix, older_post_matrix, younger_pre_matrix, younger_post_matrix = \
            tools.count_noun_adj(sentences,
                           reduced_lemma,
                           canon_nouns,
                           reduced_older,
                           reduced_younger,
                           reduced_older_pre,
                           reduced_older_post,
                           reduced_younger_pre,
                           reduced_younger_post)

        # Generate the data.
        all_data = tools.matrix_gen_csv(matrix, reduced_lemma, reduced_nouns)
        older_data = tools.matrix_gen_csv(older_matrix, reduced_lemma, reduced_nouns)
        younger_data = tools.matrix_gen_csv(younger_matrix, reduced_lemma, reduced_nouns)
        older_pre_data = tools.matrix_gen_csv(older_pre_matrix, reduced_lemma, reduced_nouns)
        older_post_data = tools.matrix_gen_csv(older_post_matrix, reduced_lemma, reduced_nouns)
        younger_pre_data = tools.matrix_gen_csv(younger_pre_matrix, reduced_lemma, reduced_nouns)
        younger_post_data = tools.matrix_gen_csv(younger_post_matrix, reduced_lemma, reduced_nouns)

        # We need to build the header.
        header = ""
        for n in reduced_nouns:
            header = header + "," + n

        # CSV-ize it!
        all_csv = tools.gen_CSV(header, all_data)
        older_csv = tools.gen_CSV(header, older_data)
        younger_csv = tools.gen_CSV(header, younger_data)
        older_pre_csv = tools.gen_CSV(header, older_pre_data)
        older_post_csv = tools.gen_CSV(header, older_post_data)
        younger_pre_csv = tools.gen_CSV(header, younger_pre_data)
        younger_post_csv = tools.gen_CSV(header, younger_post_data)

        # Output the CSV data to files.
        tools.write_CSV(all_csv, arg.output + "/matrix-all.csv")
        tools.write_CSV(older_csv, arg.output + "/matrix-older.csv")
        tools.write_CSV(younger_csv, arg.output + "/matrix-younger.csv")
        tools.write_CSV(older_pre_csv, arg.output + "/matrix-older-pre.csv")
        tools.write_CSV(older_post_csv, arg.output + "/matrix-older-post.csv")
        tools.write_CSV(younger_pre_csv, arg.output + "/matrix-younger-pre.csv")
        tools.write_CSV(younger_post_csv, arg.output + "/matrix-younger-post.csv")

        return 0

    # List of known correctly tagged adjectives.
    if arg.whitelist is None:
        arg.whitelist = arg.output + '/whitelist.txt'
    adjective_whitelist = tools.read_text(arg.whitelist)
    # List of known erroneously tagged adjectives.
    if arg.blacklist is None:
        arg.blacklist = arg.output + '/blacklist.txt'
    adjective_blacklist = tools.read_text(arg.blacklist)

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
        tools.save_text(adjective_whitelist, arg.whitelist)
        tools.save_text(adjective_blacklist, arg.blacklist)

        if os.path.isfile(arg.output + '/verified-groups.json'):
            tools.merge_JSON(sentences, arg.output + '/verified-groups.json')
        else:
            tools.save_JSON(sentences, arg.output + '/verified-groups.json')
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

        tools.save_JSON(to_verify, arg.output + '/unverified-groups.json')

        if os.path.isfile(arg.output + '/verified-groups.json'):
            tools.merge_JSON(verified, arg.output + '/verified-groups.json')
        else:
            tools.save_JSON(verified, arg.output + '/verified-groups.json')

main()