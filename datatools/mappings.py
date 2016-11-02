import operator
import numpy as np
import boolnet.bintools.packing as pk


FUNCTIONS = {
    'add':  operator.add,
    'sub':  operator.sub,
    'mul':  operator.mul,
    'div':  operator.floordiv,
    'mod':  operator.mod,
}


def to_binary(value, num_bits):
    # little-endian
    return np.flipud(np.array(
        [int(i) for i in np.binary_repr(value, num_bits)]))


def two_input_mapping(num_bits_per_operand, functor):
    # Upper limit
    upper = 2**num_bits_per_operand
    # generate dict for function
    function = {i1*upper + i2: functor(i1, i2) % upper
                for i1 in range(upper)
                for i2 in range(upper)}
    return function


def binmap_from_function(func, Ni, No):
    M = np.zeros((len(func), Ni+No), dtype=np.uint8)
    # views into M
    I, T = np.split(M, [Ni], axis=1)

    for idx, (inp, out) in enumerate(func.items()):
        I[idx] = to_binary(inp, Ni)[:Ni]
        T[idx] = to_binary(out, No)[:No]

    return pk.BitPackedMatrix(pk.pack_bool_matrix(M), M.shape[0], Ni)


def mapping_to_file(function, numbits, numout_limit, outfile):
    if not outfile:
        outfile = '{}{}.npz'.format(function, numbits)

    n = numbits

    func = two_input_mapping(n, FUNCTIONS[function])

    Ni = 2*n
    No = n
    if numout_limit:
        No = numout_limit
    Mp = binmap_from_function(func, Ni, No)
    np.savez(outfile, matrix=Mp, Ni=Ni, Ne=Mp.Ne)


def mapping_from_file(filename):
    with np.load(filename) as f:
        return pk.BitPackedMatrix(f['matrix'], f['Ne'], f['Ni'])


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


def is_valid_function(X, y):
    l = [tuple(row) for row in X]
    sorted_indices = sorted(range(len(l)), key=lambda k: l[k])

    for i0, i1 in zip(sorted_indices[:-1], sorted_indices[1:]):
        if l[i0] == l[i1] and y[i0] != y[i1]:
            return False
    return True


def ambiguous_patterns(X, y, names=None, flatten=False):
    ambiguous = []
    for duplicate_indices in duplicate_patterns(X, y):
        if len(np.unique(y[duplicate_indices])) > 1:
            # more than one target value for the same pattern
            if names is not None:
                duplicate_indices = [names[i] for i in duplicate_indices]
            if flatten:
                ambiguous.extend(duplicate_indices)
            else:
                ambiguous.append(duplicate_indices)
    return ambiguous
