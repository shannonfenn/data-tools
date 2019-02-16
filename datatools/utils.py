import numpy as np
import itertools


def inverse_permutation(permutation):
    inverse = np.zeros_like(permutation)
    for i, p in enumerate(permutation):
        inverse[p] = i
    return inverse


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


def ambiguous_patterns(X, Y, flatten=False):
    Y = Y.reshape(Y.shape[0], -1)  # cast vectors to nx1 arrays
    ambiguous = (batch
                 for batch in duplicate_patterns(X)
                 if len(np.unique(Y[batch], axis=0)) > 1)

    if flatten:
        ambiguous = itertools.chain.from_iterable(ambiguous)

    return list(ambiguous)
