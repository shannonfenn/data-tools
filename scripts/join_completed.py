#! /usr/bin/env python

import argparse
import pandas as pd
import numpy as np


def check_dataframe(filename, data_frame, key_columns):
    if any(col not in data_frame for col in key_columns):
        raise ValueError('Key columns not in {}.'.format(filename))
    nonzero = np.count_nonzero(data_frame['trg_error'])
    if nonzero:
        print('Warning, some failed runs in {}.'.format(filename))


def join_completed(filenames, key_columns=None):
    completed = None
    # build single dataframe of successful runs
    for filename in filenames:
        df = pd.read_json(filename)
        check_dataframe(df, key_columns)
        if completed is None:
            completed = df[df['trg_error'] == 0]
        else:
            completed = pd.concat([completed, df[df['trg_error'] == 0]],
                                  ignore_index=True)
    # check if rows are unique on given columns
    if key_columns:
        completed.sort(key_columns)
        duplicated = completed.duplicated(key_columns).sum()
        if duplicated > 0:
            raise ValueError('Duplicate rows: {}'.format(duplicated))
    return completed


def main():
    parser = argparse.ArgumentParser(
        description='Join results with zero training error.')
    parser.add_argument('-i', type=str, nargs='+', required=True,
                        help='list of input files')
    parser.add_argument('-o', type=str, required=True,
                        help='file to store result')

    args = parser.parse_args()

    join_completed(args.i).to_json(args.o)


if __name__ == '__main__':
    main()
