# Miscellaneous tools to help process thesis data.

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

def count_from_list(data, adjectives):
    """
    Generations a dictionary list of adjectives and their prenominal / postnominal counts.

    :param data: A list of sentence objects.
    :param adjectives: A list of adjectives
    :return: A dictionary in the format of count{adjective} = (prenominal, postnominal)
    """
    # Going to store the data in a dictionary of tuples.  Each adjective will
    # have an entry and that entry will have a tuple of (pre, post) for that
    # adjective.
    counts = {}

    # Go through each adjective and all the sentences looking for said adjective.
    for adjective in adjectives:
        # Initialize counter variables.
        pre_count = 0
        post_count = 0

        # Count the adjectives found in each position for each sentence.
        for sentence in data:
            this_pre_count, this_post_count = sentence.get_adjective_count(adjective)
            pre_count += this_pre_count
            post_count += this_post_count

        counts[adjective] = (pre_count, post_count)

    return counts