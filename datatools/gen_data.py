import argparse
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


def dump(func, Ni, No, outfile):
    M = np.zeros((len(func), Ni+No), dtype=np.uint8)
    # views into M
    I, T = np.split(M, [Ni], axis=1)

    for idx, (inp, out) in enumerate(func.items()):
        I[idx] = to_binary(inp, Ni)[:Ni]
        T[idx] = to_binary(out, No)[:No]

    Mp = pk.pack_bool_matrix(M)

    np.savez(outfile, matrix=Mp, Ni=Ni, Ne=M.shape[0])


def main(args):
    if args.outfile:
        out = args.outfile
    else:
        out = '{}{}.npz'.format(args.function, args.numbits)

    n = args.numbits

    func = two_input_mapping(n, FUNCTIONS[args.function])

    Ni = 2*n
    No = n
    if args.outlim:
        No = args.outlim
    dump(func, Ni, No, out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate json file for given function.')
    parser.add_argument('numbits', type=int,
                        help='number of input bits per operand')
    parser.add_argument('function', metavar='function',
                        choices=FUNCTIONS.keys(),
                        help='function to generate data for, one of: {}.'.
                        format(list(FUNCTIONS.keys())))
    parser.add_argument('--outfile', type=str,
                        help=('output filename - if omitted will default '
                              'to [function][n].npz'))
    parser.add_argument('--outlim', metavar='k', type=int,
                        help=('(optional) number of bits to limit output to, '
                              'takes the k least significant.'))

    main(parser.parse_args())
