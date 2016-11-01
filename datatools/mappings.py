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


def unique_rows(M):
    uniq = np.unique(M.view(M.dtype.descr * M.shape[1]))
    return uniq.view(M.dtype).reshape(-1, M.shape[1])


def validate_mapping(M):
    # check input and target dimensions are sensible
    assert 0 < M.Ni < M.shape[0]
    # check example number is sensible
    assert 0 < M.Ne <= M.shape[1]
