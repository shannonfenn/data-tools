import datatools.ranking as rk
import numpy as np


def inverse_permutation(permutation):
    inverse = np.zeros_like(permutation)
    for i, p in enumerate(permutation):
        inverse[p] = i
    return inverse


def overlap(A, B):
    A, B = set(A), set(B)
    if len(A) == 0 or len(B) == 0:
        return 0
    return len(A & B) / min(len(A), len(B))


def nestedness(F):
    # F is assumed to be ordered
    O = [overlap(f1, f2) for f1, f2 in zip(F[:-1], F[1:])]
    return sum(O) / len(O)


def cardinality_rank(cardinalities, break_ties=False):
    return rk.cost_rank(cardinalities, break_ties)


def unique_rows(X):
    uniq = np.unique(X.view(X.dtype.descr * X.shape[1]))
    return uniq.view(X.dtype).reshape(-1, X.shape[1])


def duplicate_patterns(X, names=None):
    l = [tuple(row) for row in X]
    sorted_indices = sorted(range(len(l)), key=lambda k: l[k])

    if names is None:
        # identity function to give indices when names not given
        names = list(range(len(sorted_indices)))

    duplicates = []
    run_found = False
    for i0, i1 in zip(sorted_indices[:-1], sorted_indices[1:]):
        if l[i0] == l[i1]:
            if not run_found:
                # start new list
                duplicates.append([names[i0], names[i1]])
            else:
                duplicates[-1].append(names[i1])
            run_found = True
        else:
            run_found = False

    return duplicates


def is_valid_function(X, y, verbose=False):
    l = [tuple(row) for row in X]
    sorted_indices = sorted(range(len(l)), key=lambda k: l[k])

    for i0, i1 in zip(sorted_indices[:-1], sorted_indices[1:]):
        if l[i0] == l[i1] and y[i0] != y[i1]:
            if verbose:
                print('{} ({}->{}) and {} ({}->{}) not separated'.format(
                    i0, l[i0], y[i0], i1, l[i1], y[i1]))
            return False
    return True


def ambiguous_patterns(X, y, names=None, flatten=False):
    ambiguous = []
    for duplicate_indices in duplicate_patterns(X):
        if len(np.unique(y[duplicate_indices])) > 1:
            # more than one target value for the same pattern
            if names is not None:
                duplicate_indices = [names[i] for i in duplicate_indices]
            if flatten:
                ambiguous.extend(duplicate_indices)
            else:
                ambiguous.append(duplicate_indices)
    return ambiguous
