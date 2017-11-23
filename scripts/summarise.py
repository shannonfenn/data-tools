#! /usr/bin/env python

import numpy as np
import pandas as pd
import functools
import argparse
# from statsmodels.stats import api as sms

# def conf95u(x):
#     return sms.DescrStatsW(x).tconfint_mean(0.05)[1]
#
# def conf99u(x):
#     return sms.DescrStatsW(x).tconfint_mean(0.01)[1]
#
# def conf999u(x):
#     return sms.DescrStatsW(x).tconfint_mean(0.001)[1]
#
# def conf95l(x):
#     return sms.DescrStatsW(x).tconfint_mean(0.05)[0]
#
# def conf99l(x):
#     return sms.DescrStatsW(x).tconfint_mean(0.01)[0]
#
# def conf999l(x):
#     return sms.DescrStatsW(x).tconfint_mean(0.001)[0]


# code to change for using to calculate AUC style measures

def trapz(y, df, x_series):
    x = df.iloc[y.index][x_series]
    return np.trapz(y, x=x)


def summarise(df, key_columns, val_columns, aggregators):
    df['treatment'] = df[key_columns[0]].apply(str)
    for c in key_columns[1:]:
        df['treatment'] += ' / ' + df[c].apply(str)

    for v in val_columns:
        # sum list-values, pass-through others
        df[v] = df[v].apply(lambda x: sum(x) if isinstance(x, list) else x)

    df_long = pd.melt(df, id_vars=['treatment', 'Ne'], value_vars=val_columns)

    grp = df_long.groupby(['variable', 'treatment', 'Ne'])

    grp = grp['value'].agg(aggregators).reset_index()

    cumulative = functools.partial(trapz, df=grp, x_series='Ne')
    g2 = grp.groupby(['variable', 'treatment'])
    return g2.agg(cumulative).drop('Ne', axis=1)


def main():
    default_key_columns = ['learner', 'guiding_function']
    default_val_columns = ['trg_mcc', 'test_mcc', 'learning_time']
    default_aggregators = ['count', 'min', 'mean', 'max']

    parser = argparse.ArgumentParser(
        description='Summarise results with cumulative scores.')
    parser.add_argument('infile', type=argparse.FileType())
    parser.add_argument('--key-columns', '-k', type=str, nargs='+',
                        metavar='str', default=default_key_columns,
                        help='default: ' + ' '.join(default_key_columns))
    parser.add_argument('--val-columns', '-v', type=str, nargs='+',
                        metavar='str', default=default_val_columns,
                        help='default: ' + ' '.join(default_val_columns))
    parser.add_argument('--aggregators', '-a', type=str, nargs='+',
                        metavar='str', default=default_aggregators,
                        help='default: ' + ' '.join(default_aggregators))
    args = parser.parse_args()

    df = pd.read_json(args.infile)

    pd.set_option('display.precision', 3)

    print(summarise(df, args.key_columns, args.val_columns, args.aggregators))


if __name__ == '__main__':
    main()
