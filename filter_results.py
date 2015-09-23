import numpy as np
import pandas as pd
import easygui
import argparse


def get_results(filename=None):
    if not filename:
        filename = easygui.fileopenbox()
    return pd.read_json(filename)


def get_No(data):
    if data.No.min() == data.No.max():
        return data.No.min()
    else:
        raise ValueError('Non-uniform No')


def aggregate_generalised(results):
    No = get_No(results)
    for t in range(No):
        target_generalised = results['test_err_tgt_{}'.format(t)] == 0
        results['gen_tgt_{}'.format(t)] = target_generalised

    results['gen'] = results.gen_tgt_0
    for t in range(1, No):
        results.gen = results.gen & results['gen_tgt_{}'.format(t)]

    grouped = results.groupby(['optimiser_guiding_function', 'Ne'])
    cols_to_keep = {'gen_tgt_{}'.format(t): np.mean for t in range(No)}
    cols_to_keep.update({'test_err_tgt_{}'.format(t): np.mean
                         for t in range(No)})
    cols_to_keep['gen'] = np.mean
    cols_to_keep['test_error_simple'] = np.mean
    return grouped.aggregate(cols_to_keep).reset_index()


def main():
    # scores: generalisation probability and mean generalisation error
    columns = ['learner', 'optimiser_guiding_function', 'Ne']
    parser = argparse.ArgumentParser(
        description='Calculate generalisation measures for each combination.')
    parser.add_argument('infile', type=str)
    parser.add_argument('outfile', type=str)
    parser.add_argument('--key-columns', type=list)

    args = parser.parse_args()
    completed_df = join_completed([pd.read_json(f) for f in args.files])

    completed_df.to_json(args.outfile)
lah
    results_list = [get_results('/home/shannon/HMRI/experiments/results/Varying Ne/add4_Ns1k_15-08-31_SET{}/results.json'.format(i)) for i in range(1, 4)]
    # completed = join_completed(results_list)
    # print(completed.Ne.value_counts())
    # print(completed.optimiser_guiding_function.value_counts())
    gen_data = aggregate_generalised(join_completed(results_list))


if __name__ == '__main__':
    main()

