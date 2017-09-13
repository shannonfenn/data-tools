#! /usr/bin/env python

import pandas as pd
import datatools.analysis as an
import argparse
from os.path import splitext


def main():
    # scores: generalisation probability and mean generalisation error
    default_key_columns = ['learner', 'guiding_function', 'Ne']
    parser = argparse.ArgumentParser(
        description='Calculate generalisation measures for each combination.')
    parser.add_argument('infile', type=str)
    parser.add_argument('outfile', nargs='?', type=str,
                        help='defaults to \'<infile>_aggregated.json\'')
    parser.add_argument('--key-columns', type=str, nargs='+',
                        default=default_key_columns)
    args = parser.parse_args()

    if args.outfile is None:
        base, ext = splitext(args.infile)
        args.outfile = base + '_aggregated' + ext

    df = pd.read_json(args.infile)

    df = an.aggregate_runs(df, args.key_columns)

    df.to_json(args.outfile, orient='records')


if __name__ == '__main__':
    main()
