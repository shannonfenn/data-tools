import numpy as np
import pandas as pd
import argparse
import os


def get_Ni(data):
    if data.Ni.min() == data.Ni.max():
        return data.Ni.min()
    else:
        raise ValueError('Non-uniform Ni')


def get_No(data):
    if data.No.min() == data.No.max():
        return data.No.min()
    else:
        raise ValueError('Non-uniform No')


def aggregate_generalised(raw, key_columns):
    No = get_No(raw)
    for t in range(No):
        target_generalised = raw['test_err_tgt_{}'.format(t)] == 0
        raw['gen_tgt_{}'.format(t)] = target_generalised
        target_memorised = raw['train_err_tgt_{}'.format(t)] == 0
        raw['mem_tgt_{}'.format(t)] = target_memorised

    raw['gen'] = raw.gen_tgt_0
    raw['mem'] = raw.mem_tgt_0
    for t in range(1, No):
        raw.gen = raw.gen & raw['gen_tgt_{}'.format(t)]
        raw.mem = raw.mem & raw['mem_tgt_{}'.format(t)]

    if not all(raw['mem']):
        print('Warning: {} configurations have not achieved memorisation!'.
              format(len(raw['mem']) - sum(raw['mem'])))

    grouped = raw.groupby(key_columns)

    unique_counts = grouped.count()['gen'].nunique()
    if unique_counts > 1:
        print('Warning: non-uniform result numbers, {} unique counts!'.
              format(unique_counts))

    # training data
    cols_to_keep = {'mem_tgt_{}'.format(t): np.mean for t in range(No)}
    cols_to_keep.update({'train_err_tgt_{}'.format(t): np.mean
                         for t in range(No)})
    cols_to_keep['mem'] = np.mean
    cols_to_keep['training_error_simple'] = [np.mean, np.std]
    # test data
    cols_to_keep.update({'gen_tgt_{}'.format(t): np.mean for t in range(No)})
    cols_to_keep.update({'test_err_tgt_{}'.format(t): np.mean
                         for t in range(No)})
    cols_to_keep['gen'] = np.mean
    cols_to_keep['test_error_simple'] = [np.mean, np.std]

    aggregated = grouped.aggregate(cols_to_keep).reset_index()

    # collapse the multi-index columns by concatenating the names
    aggregated.columns = [' '.join(col).strip().replace(' ', '_')
                          for col in aggregated.columns.values]

    aggregated['No'] = No

    # record normalised sample size
    Ni = get_Ni(raw)
    aggregated['s'] = aggregated.Ne / 2**Ni

    return aggregated


def main():
    # scores: generalisation probability and mean generalisation error
    default_key_columns = ['learner', 'optimiser_guiding_function', 'Ne']
    parser = argparse.ArgumentParser(
        description='Calculate generalisation measures for each combination.')
    parser.add_argument('file', type=str)
    parser.add_argument('--outfile', '-o', type=str)
    parser.add_argument('--key-columns', type=str, nargs='+',
                        default=default_key_columns)

    args = parser.parse_args()

    df = pd.read_json(args.file)

    df = aggregate_generalised(df, args.key_columns)

    if args.outfile:
        outfile = args.outfile
    else:
        base, ext = os.path.splitext(args.file)
        outfile = base + '_gen' + ext

    df.to_json(outfile, orient='records')


if __name__ == '__main__':
    main()
