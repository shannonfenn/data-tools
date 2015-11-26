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


def mean_non_zero(col):
    return np.ma.masked_values(col, 0.0, rtol=0, copy=False).mean()


def accuracy(orders):
    CM = confusion_matrix(orders)
    if CM is None:
        return None
    else:
        return CM.trace() / CM.sum()


def confusion_matrix(orders):
    # if there are None/NaNs in the array then there is no valid CM
    if orders.isnull().values.any():
        return None

    # we want a 2D array from the incoming pandas series of lists
    orders = np.array(orders.tolist())

    num_vals = orders.shape[1]

    # an orders array with values outside [0, num_vals)
    # indicates a pretty big problem
    if orders.max() >= num_vals or orders.min() < 0:
        raise ValueError('Input array has values outside [0, num_vals)')

    CM = np.zeros((num_vals, num_vals), dtype=int)
    for i in range(num_vals):
        indices, counts = np.unique(orders[:, i], return_counts=True)
        CM[i, indices] = counts
    return CM


def confusion_matrix_reducer(orders):
    CM = confusion_matrix(orders)
    if CM is not None:
        CM = CM.tolist()
    return CM


def aggregate_runs(raw, key_columns):
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

    # check that all configurations have memorised
    if not all(raw['mem']):
        print('Warning: {} configurations have not achieved memorisation!'.
              format(len(raw['mem']) - sum(raw['mem'])))

    grouped = raw.groupby(key_columns)

    # training data
    cols_to_keep = dict()
    cols_to_keep['training_error_simple'] = [np.mean, np.std, mean_non_zero]
    cols_to_keep['mem'] = np.mean
    cols_to_keep.update(
        {'mem_tgt_{}'.format(t): np.mean for t in range(No)})
    cols_to_keep.update(
        {'train_err_tgt_{}'.format(t): [np.mean, np.std, mean_non_zero]
         for t in range(No)})
    # test data
    cols_to_keep['test_error_simple'] = [np.mean, np.std, mean_non_zero]
    cols_to_keep['gen'] = np.mean
    cols_to_keep.update(
        {'gen_tgt_{}'.format(t): np.mean for t in range(No)})
    cols_to_keep.update(
        {'test_err_tgt_{}'.format(t): [np.mean, np.std, mean_non_zero]
         for t in range(No)})

    if 'target_order' in raw:
        cols_to_keep['target_order'] = [confusion_matrix_reducer, accuracy]

    aggregated = grouped.aggregate(cols_to_keep).reset_index()

    # collapse the multi-index columns by concatenating the names
    aggregated.columns = [' '.join(col).strip().replace(' ', '_')
                          for col in aggregated.columns.values]

    # Scores defined by Goudarzi et. al.
    aggregated['training_score'] = 1 - aggregated.training_error_simple_mean
    aggregated['generalisation_score'] = 1 - aggregated.test_error_simple_mean
    for i in range(No):
        src_key = 'train_err_tgt_{}_mean'.format(i)
        new_key = 'trg_score_tgt_{}'.format(i)
        aggregated[new_key] = 1 - aggregated[src_key]
        src_key = 'test_err_tgt_{}_mean'.format(i)
        new_key = 'gen_score_tgt_{}'.format(i)
        aggregated[new_key] = 1 - aggregated[src_key]

    # scores for non-generalised cases
    aggregated['training_score_non_zero'] = 1 - aggregated.training_error_simple_mean_non_zero
    aggregated['generalisation_score_non_zero'] = 1 - aggregated.test_error_simple_mean_non_zero
    for i in range(No):
        src_key = 'train_err_tgt_{}_mean_non_zero'.format(i)
        new_key = 'trg_score_tgt_{}_non_zero'.format(i)
        aggregated[new_key] = 1 - aggregated[src_key]
        src_key = 'test_err_tgt_{}_mean_non_zero'.format(i)
        new_key = 'gen_score_tgt_{}_non_zero'.format(i)
        aggregated[new_key] = 1 - aggregated[src_key]

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
    parser.add_argument('--outfile', '-o', type=str,
                        help='defaults to input filename with \'_gen\''
                             ' appended.')
    parser.add_argument('--key-columns', type=str, nargs='+',
                        default=default_key_columns)

    args = parser.parse_args()

    df = pd.read_json(args.file)

    df = aggregate_runs(df, args.key_columns)

    if args.outfile:
        outfile = args.outfile
    else:
        base, ext = os.path.splitext(args.file)
        outfile = base + '_gen' + ext

    df.to_json(outfile, orient='records')


if __name__ == '__main__':
    main()