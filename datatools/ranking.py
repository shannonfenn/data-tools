import numpy as np
import scipy.stats as st
import scipy.spatial.distance as dst
import minfs.feature_selection as fss


def break_rank_ties(ranking):
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
    rank = fss.order_to_ranking_with_ties(
        order, lambda i1, i2: costs[i1] == costs[i2])
    if break_ties:
        rank = break_rank_ties(rank)
    return rank


def kendalltau(p, q):
    return st.kendalltau(p, q)[0]


def manh(p, q):
    return dst.cityblock(p, q)


def hamm(p, q):
    return dst.hamming(p, q)


def num_decreases(p, q):
    return sum(v1 > v2 for v1, v2 in zip(p[q][:-1], p[q][1:]))