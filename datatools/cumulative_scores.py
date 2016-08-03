import numpy as np
import pandas as pd
import argparse


def get_No(data):
    if data.No.min() == data.No.max():
        return data.No.min()
    else:
        raise ValueError('Non-uniform No')


def check_columns_in_dataframe(df, cols):
    for c in cols:
        if c not in df:
            raise ValueError('Column not in the dataframe: {}'.format(c))


def cumulative_scores(df, by, verbose):
    if isinstance(by, str):
        by = [by]
    check_columns_in_dataframe(df, by + [
        's', 'gen_mean', 'gen_score'])

    No = get_No(df)

    print('Cumulative Generalisation Probability')
    for name, group in df.groupby(by):
        full = np.trapz(group['gen_mean'], x=group['s'])
        per_tgt = [np.trapz(group['gen_tgt_{}_mean'.format(i)], x=group['s'])
                   for i in range(No)]
        print(name, ':', full, per_tgt if verbose else '')

    print('Cumulative Generalisation Score')
    for name, group in df.groupby(by):
        full = np.trapz(group['gen_score'], x=group['s'])
        per_tgt = [np.trapz(group['gen_score_tgt_{}'.format(i)], x=group['s'])
                   for i in range(No)]
        print(name, ':', full, per_tgt if verbose else '')

    print('Cumulative Generalisation Score Ignoring Zeroes')
    for name, group in df.groupby(by):
        full = np.trapz(group['gen_score_nonzero'], x=group['s'])
        per_tgt = [np.trapz(group['gen_score_tgt_{}_nonzero'.format(i)],
                            x=group['s'])
                   for i in range(No)]
        print(name, ':', full, per_tgt if verbose else '')


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

    cumulative_scores(df, 'guiding_function', args.v)


if __name__ == '__main__':
    main()
