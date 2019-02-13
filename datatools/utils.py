import numpy as np
import itertools
import functools


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


# for calculating AUC style measures
def norm_trapz(y):
    x = y.index
    width = x.max() - x.min()
    if width == 0:
        return np.nan
    return np.trapz(y, x=x) / width


def cumulative_pre_aggregate(df, kdims, vdim, idim, aggregators):
    def _old_norm_trapz(y, df, x_series):
        x = df.iloc[y.index][x_series]
        if x.max() == x.min():
            return np.nan
        return np.trapz(y, x=x) / (x.max() - x.min())
    if isinstance(aggregators, list):
        aggregators = {f.__name__: f for f in aggregators}
    grp = df.groupby(kdims + [idim])[vdim]
    grp = grp.agg(aggregators.values()).reset_index()
    grp = grp.rename(columns={func.__name__: new_name
                              for new_name, func in aggregators.items()})
    summary = grp.groupby(kdims).agg(
        functools.partial(_old_norm_trapz, df=grp, x_series=idim))
    summary.drop(columns=idim, inplace=True)
    return summary.reset_index()


def cumulative_sample(df, kdims, vdims, idim):
    df = df.set_index(idim)
    df = df.sort_index()
    grouped = df.groupby(kdims)[vdims]
    summary = grouped.agg(norm_trapz)
    return summary.reset_index()
