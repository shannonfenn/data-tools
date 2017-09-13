#! /usr/bin/env python

import pandas as pd
import argparse
import datatools.analysis as an


def main():
    # scores: generalisation probability and mean generalisation error
    parser = argparse.ArgumentParser(
        description='Calculate cumulative generalisation measures for each '
                    'guiding function.')
    parser.add_argument('file', type=str)
    parser.add_argument('-v', action='store_true',
                        help='verbose: include scores per target.')
    # parser.add_argument('--independant-var', '-i', type=str, nargs='+',
    #                     default=default_ind_var)

    args = parser.parse_args()

    df = pd.read_json(args.file)

    cumulative = an.cumulative_scores(df, 'guiding_function', args.v)

    print(cumulative)

if __name__ == '__main__':
    main()
