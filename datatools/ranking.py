import numpy as np
import scipy.stats as st
import scipy.spatial.distance as dst
import itertools


def dataset_pairs(ds_name):
    if ds_name.startswith('BT8'):
        return [(4, 0), (4, 1), (5, 2), (5, 3), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5)]
    elif ds_name.startswith('BT16'):
        return [(8, 0), (8, 1), (9, 2), (9, 3), (10, 4), (10, 5), (11, 6), (11, 7), (12, 0), (12, 1), (12, 2), (12, 3), (12, 8), (12, 9), (13, 4), (13, 5), (13, 6), (13, 7), (13, 10), (13, 11), (14, 0), (14, 1), (14, 2), (14, 3), (14, 4), (14, 5), (14, 6), (14, 7), (14, 8), (14, 9), (14, 10), (14, 11), (14, 12), (14, 13)]
    elif ds_name.startswith('Trell5'):
        return [(4, 0), (4, 1), (5, 1), (5, 2), (6, 2), (6, 3), (7, 0), (7, 1), (7, 2), (7, 4), (7, 5), (8, 1), (8, 2), (8, 3), (8, 5), (8, 6), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8)]
    elif ds_name.startswith('Trell6'):
        return [(5, 0), (5, 1), (6, 1), (6, 2), (7, 2), (7, 3), (8, 3), (8, 4), (9, 0), (9, 1), (9, 2), (9, 5), (9, 6), (10, 1), (10, 2), (10, 3), (10, 6), (10, 7), (11, 2), (11, 3), (11, 4), (11, 7), (11, 8), (12, 0), (12, 1), (12, 2), (12, 3), (12, 5), (12, 6), (12, 7), (12, 9), (12, 10), (13, 1), (13, 2), (13, 3), (13, 4), (13, 6), (13, 7), (13, 8), (13, 10), (13, 11), (14, 0), (14, 1), (14, 2), (14, 3), (14, 4), (14, 5), (14, 6), (14, 7), (14, 8), (14, 9), (14, 10), (14, 11), (14, 12), (14, 13)]
    elif ds_name.startswith('Trell7'):
        return [(6, 0), (6, 1), (7, 1), (7, 2), (8, 2), (8, 3), (9, 3), (9, 4), (10, 4), (10, 5), (11, 0), (11, 1), (11, 2), (11, 6), (11, 7), (12, 1), (12, 2), (12, 3), (12, 7), (12, 8), (13, 2), (13, 3), (13, 4), (13, 8), (13, 9), (14, 3), (14, 4), (14, 5), (14, 9), (14, 10), (15, 0), (15, 1), (15, 2), (15, 3), (15, 6), (15, 7), (15, 8), (15, 11), (15, 12), (16, 1), (16, 2), (16, 3), (16, 4), (16, 7), (16, 8), (16, 9), (16, 12), (16, 13), (17, 2), (17, 3), (17, 4), (17, 5), (17, 8), (17, 9), (17, 10), (17, 13), (17, 14), (18, 0), (18, 1), (18, 2), (18, 3), (18, 4), (18, 6), (18, 7), (18, 8), (18, 9), (18, 11), (18, 12), (18, 13), (18, 15), (18, 16), (19, 1), (19, 2), (19, 3), (19, 4), (19, 5), (19, 7), (19, 8), (19, 9), (19, 10), (19, 12), (19, 13), (19, 14), (19, 16), (19, 17), (20, 0), (20, 1), (20, 2), (20, 3), (20, 4), (20, 5), (20, 6), (20, 7), (20, 8), (20, 9), (20, 10), (20, 11), (20, 12), (20, 13), (20, 14), (20, 15), (20, 16), (20, 17), (20, 18), (20, 19)]
    elif ds_name.startswith('Trell8'):
        return [(7, 0), (7, 1), (8, 1), (8, 2), (9, 2), (9, 3), (10, 3), (10, 4), (11, 4), (11, 5), (12, 5), (12, 6), (13, 0), (13, 1), (13, 2), (13, 7), (13, 8), (14, 1), (14, 2), (14, 3), (14, 8), (14, 9), (15, 2), (15, 3), (15, 4), (15, 9), (15, 10), (16, 3), (16, 4), (16, 5), (16, 10), (16, 11), (17, 4), (17, 5), (17, 6), (17, 11), (17, 12), (18, 0), (18, 1), (18, 2), (18, 3), (18, 7), (18, 8), (18, 9), (18, 13), (18, 14), (19, 1), (19, 2), (19, 3), (19, 4), (19, 8), (19, 9), (19, 10), (19, 14), (19, 15), (20, 2), (20, 3), (20, 4), (20, 5), (20, 9), (20, 10), (20, 11), (20, 15), (20, 16), (21, 3), (21, 4), (21, 5), (21, 6), (21, 10), (21, 11), (21, 12), (21, 16), (21, 17), (22, 0), (22, 1), (22, 2), (22, 3), (22, 4), (22, 7), (22, 8), (22, 9), (22, 10), (22, 13), (22, 14), (22, 15), (22, 18), (22, 19), (23, 1), (23, 2), (23, 3), (23, 4), (23, 5), (23, 8), (23, 9), (23, 10), (23, 11), (23, 14), (23, 15), (23, 16), (23, 19), (23, 20), (24, 2), (24, 3), (24, 4), (24, 5), (24, 6), (24, 9), (24, 10), (24, 11), (24, 12), (24, 15), (24, 16), (24, 17), (24, 20), (24, 21), (25, 0), (25, 1), (25, 2), (25, 3), (25, 4), (25, 5), (25, 7), (25, 8), (25, 9), (25, 10), (25, 11), (25, 13), (25, 14), (25, 15), (25, 16), (25, 18), (25, 19), (25, 20), (25, 22), (25, 23), (26, 1), (26, 2), (26, 3), (26, 4), (26, 5), (26, 6), (26, 8), (26, 9), (26, 10), (26, 11), (26, 12), (26, 14), (26, 15), (26, 16), (26, 17), (26, 19), (26, 20), (26, 21), (26, 23), (26, 24), (27, 0), (27, 1), (27, 2), (27, 3), (27, 4), (27, 5), (27, 6), (27, 7), (27, 8), (27, 9), (27, 10), (27, 11), (27, 12), (27, 13), (27, 14), (27, 15), (27, 16), (27, 17), (27, 18), (27, 19), (27, 20), (27, 21), (27, 22), (27, 23), (27, 24), (27, 25), (27, 26)]
    else:
        return None


def order_to_ranking_with_ties(order, tied):
    # build ranking from the above order (with ties)
    ranking = np.zeros(len(order), dtype=int)

    # check ranking from 2nd element in order
    # first element is rank 0 automatically by np.zeros
    for i in range(1, len(order)):
        i1 = order[i-1]
        i2 = order[i]
        if tied(i1, i2):
            # tie - continuing using current ranking
            ranking[i2] = ranking[i1]
        else:
            ranking[i2] = i
    return ranking


def rank_with_ties_broken(ranking):
    ranking = np.array(ranking, copy=True)
    for r in range(ranking.size):
        # find all tied indices
        indices = np.where(ranking == r)[0]
        if indices.size > 1:
            # randomly reassign all matching
            ranking[np.random.permutation(indices)] = np.arange(
                r, r+indices.size)
    return ranking


def cost_rank(costs, break_ties=False):
    # sort by cardinality
    order = np.argsort(costs)
    # convert this to a ranking - accounting for ties in cardinality
    rank = order_to_ranking_with_ties(
        order, lambda i1, i2: costs[i1] == costs[i2])
    if break_ties:
        rank = rank_with_ties_broken(rank)
    return rank


def inverse_permutation(permutation):
    inverse = np.zeros_like(permutation)
    for i, p in enumerate(permutation):
        inverse[p] = i
    return inverse


def kendalltau(p, q, pairs=None):
    if pairs is None:
        return st.kendalltau(p, q)[0]
    else:
        d = kendalltau_distance(p, q, pairs)
        return 1 - 2 * d / len(pairs)


def partial_tau(pairs, ref_pairs):
    raise NotImplementedError
    # fails if perm is not a permutation
    inverse_pairs = {(j, i) for i, j in pairs}
    concordant = set(pairs) & set(ref_pairs)
    discordant = set(inverse_pairs) & set(ref_pairs)
    distance = len(concordant) - len(discordant)
#     return concordant, discordant
    return distance / len(ref_pairs)


def kendalltau_distance(p, q, pairs=None):
    if pairs is None:
        pairs = itertools.combinations(range(0, len(p)), 2)
    distance = 0
    for x, y in pairs:
        a = p[x] - p[y]
        b = q[x] - q[y]
        # if discordant (different signs)
        if (a * b < 0):
            distance += 1
    return distance


def kendall_w(rankings):
    rankings = np.asarray(rankings)
    if rankings.ndim != 2:
        raise ValueError('ratings matrix must be 2-dimensional')
    m = rankings.shape[0]  # raters
    n = rankings.shape[1]  # items rated
    denom = m**2 * (n**3 - n)
    ranking_sums = np.sum(rankings, axis=0)
    S = n * np.var(ranking_sums)
    return 12 * S / denom


def manh(p, q):
    return dst.cityblock(p, q)


def hamm(p, q):
    return dst.hamming(p, q)


def num_decreases(p, q):
    return sum(v1 > v2 for v1, v2 in zip(p[q][:-1], p[q][1:]))


def pairs_from_total_order(order):
    return [(order[i], order[j]) for i in range(len(order)) for j in range(i+1, len(order))]
