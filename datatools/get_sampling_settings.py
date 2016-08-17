import argparse
import pandas as pd
import numpy as np
import sys


def get_sampling_settings(df):
    Ni_values = np.unique(df.Ni)
    if len(Ni_values) > 1:
        print('More than one Ni')
        sys.exit()

    Ni = Ni_values[0]
    Ne_values = np.unique(df.Ne)
    Ne_seed_pairs = []

    for Ne in Ne_values:
        seeds = np.unique(df[df.Ne == Ne].sample_seed)
        if len(seeds) > 1:
            print('More than one ({}) seed for Ne = {}'.format(
                len(seeds), Ne))
            sys.exit()
        Ne_seed_pairs.append((Ne, seeds[0]))

    return Ni, Ne_seed_pairs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('r'))
    args = parser.parse_args()

    df = pd.read_json(args.file)
    Ni, Ne_seed_pairs = get_sampling_settings(df)
    print(Ni, Ne_seed_pairs)
