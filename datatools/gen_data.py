import argparse
import operator
import numpy as np


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
    inps = np.zeros((len(func), Ni), dtype=np.uint8)
    tgts = np.zeros((len(func), No), dtype=np.uint8)

    for idx, inp, out in enumerate(func.items()):
        inps[idx] = to_binary(inp, Ni)[:Ni]
        tgts[idx] = to_binary(out, No)[:No]

    np.savez(outfile, input_matrix=inps, target_matrix=tgts)


def main(args):
    if args.outfile:
        out = args.outfile
    else:
        out = 'functions/{}{}.npz'.format(args.function, args.numbits)

    n = args.numbits

    func = two_input_mapping(n, FUNCTIONS[args.function])

    Ni = 2*n
    No = n
    if args.outlim:
        No = args.outlim
    with open(out, 'w') as outfile:
        dump(func, Ni, No, outfile)


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
                              'to functions/[function][n].npz'))
    parser.add_argument('--outlim', metavar='k', type=int,
                        help=('(optional) number of bits to limit output to, '
                              'takes the k least significant.'))

    main(parser.parse_args())
