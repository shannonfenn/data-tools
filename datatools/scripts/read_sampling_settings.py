import argparse
import pandas as pd
from datatools.analysis import sampling_settings


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('r'))
    args = parser.parse_args()

    df = pd.read_json(args.file)
    Ni, Ne_seed_pairs = sampling_settings(df)
    print(Ni, Ne_seed_pairs)
