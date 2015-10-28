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


def cumulative_scores(df, by):
    if isinstance(by, str):
        by = [by]
    check_columns_in_dataframe(df, by + [
        's', 'gen_mean', 'generalisation_score'])

    print('Cumulative Generalisation Probability')
    for name, group in df.groupby(by):
        print(name, ':', np.trapz(group['gen_mean'], x=group['s']))

    print('Cumulative Generalisation Score')
    for name, group in df.groupby(by):
        print(name, ':', np.trapz(group['generalisation_score'],
                                  x=group['s']))


def main():
    # scores: generalisation probability and mean generalisation error
    parser = argparse.ArgumentParser(
        description='Calculate cumulative generalisation measures for each '
                    'guiding function.')
    parser.add_argument('file', type=str)
    # parser.add_argument('--independant-var', '-i', type=str, nargs='+',
    #                     default=default_ind_var)

    args = parser.parse_args()

    df = pd.read_json(args.file)

    cumulative_scores(df, 'optimiser_guiding_function')


if __name__ == '__main__':
    main()
