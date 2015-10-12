import numpy as np
import pandas as pd
import argparse
import os


def get_No(data):
    if data.No.min() == data.No.max():
        return data.No.min()
    else:
        raise ValueError('Non-uniform No')


def aggregate_generalised(results, key_columns):
    No = get_No(results)
    for t in range(No):
        target_generalised = results['test_err_tgt_{}'.format(t)] == 0
        results['gen_tgt_{}'.format(t)] = target_generalised
        target_memorised = results['train_err_tgt_{}'.format(t)] == 0
        results['mem_tgt_{}'.format(t)] = target_memorised

    results['gen'] = results.gen_tgt_0
    results['mem'] = results.mem_tgt_0
    for t in range(1, No):
        results.gen = results.gen & results['gen_tgt_{}'.format(t)]
        results.mem = results.mem & results['mem_tgt_{}'.format(t)]

    if not all(results['mem']):
        print('Warning: {} configurations have not achieved memorisation!'.
              format(len(results['mem']) - sum(results['mem'])))

    grouped = results.groupby(key_columns)

    unique_counts = grouped.count()['gen'].nunique()
    if unique_counts > 1:
        print('Warning: non-uniform result numbers, {} unique counts!'.
              format(unique_counts))

    cols_to_keep = {'gen_tgt_{}'.format(t): np.mean for t in range(No)}
    cols_to_keep.update({'test_err_tgt_{}'.format(t): np.mean
                         for t in range(No)})
    cols_to_keep['gen'] = np.mean
    cols_to_keep['test_error_simple'] = [np.mean, np.std]

    df = grouped.aggregate(cols_to_keep).reset_index()

    # collapse the multi-index columns by concatenating the names
    df.columns = [' '.join(col).strip().replace(' ', '_')
                  for col in df.columns.values]

    df['No'] = No

    return df


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
