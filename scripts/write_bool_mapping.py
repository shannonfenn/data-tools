#! /usr/bin/env python

import argparse
import datatools.mappings as mp

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate json file for given function.')
    parser.add_argument('numbits', type=int,
                        help='number of input bits per operand')
    parser.add_argument('function', metavar='function',
                        choices=mp.FUNCTIONS.keys(),
                        help='function to generate data for, one of: {}.'.
                        format(list(mp.FUNCTIONS.keys())))
    parser.add_argument('--outfile', type=str,
                        help=('output filename - if omitted will default '
                              'to [function][n].npz'))
    parser.add_argument('--outlim', metavar='k', type=int,
                        help=('(optional) number of bits to limit output to, '
                              'takes the k least significant.'))
    args = parser.parse_args()
    mp.mapping_to_file(args.function, args.numbits, args.outlim, args.outfile)
