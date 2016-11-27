import datatools.ranking as rk
import numpy as np


def is_feature_set(M, T):
    _, Nf = M.shape
    class_0_indices = np.flatnonzero(T == 0)
    class_1_indices = np.flatnonzero(T)
    for i0 in class_0_indices:
        for i1 in class_1_indices:
            if np.array_equal(M[i0], M[i1]):
                return False
    return True


def overlap(A, B):
    A, B = set(A), set(B)
    return len(A & B) / min(len(A), len(B))


def nestedness(F):
    # F is assumed to be ordered
    O = [overlap(f1, f2) for f1, f2 in zip(F[:-1], F[1:])]
    return sum(O) / len(O)


def cardinality_rank(cardinalities, break_ties=False):
    return rk.cost_rank(cardinalities, break_ties)
