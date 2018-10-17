#! /usr/bin/env python

import argparse
import pandas as pd


def format_row(row):
    return f'    - {{sampling: {{Ne: {row.Ne}, seed: {row.sample_seed}}}}}'


def get_seeds(table, ignore_multiple):
    table = df.groupby('Ne').sample_seed.apply(
        lambda n: sorted(set(n), key=list(n).count)[::-1])
    assert ignore_multiple or all(table.apply(len) == 1)
    return table.apply(lambda l: l[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str)
    parser.add_argument('-y', '--yaml-out', action='store_true',
                        help='print output in yaml ready list.')
    parser.add_argument('-m', '--ignore-multiple', action='store_true',
                        help='ignore errors related to multiple seeds.')
    args = parser.parse_args()

    if args.file.endswith('.feather'):
        df = pd.read_feather(args.file)
    else:
        df = pd.read_json(args.file, lines=True)

    if args.yaml_out:
        table = get_seeds(df, args.ignore_multiple)
        table = table.reset_index().apply(format_row, axis=1)
        print('\n'.join(table.values))
    else:
        print(df.groupby('Ne').sample_seed.apply(pd.unique))
