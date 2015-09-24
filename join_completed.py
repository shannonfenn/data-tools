import pandas as pd
import ggplot as gg
import argparse
from sys import stderr


def find_failed(list_of_results):
    failed = results[results['training_error_simple'] > 0]
    for gf in sorted(set(failed.optimiser_guiding_function)):
        for Ne in sorted(set(failed.Ne)):
            indices = failed[(failed.Ne == Ne) & (failed.optimiser_guiding_function == gf)].training_set_number
            if len(indices) > 0:
                print(gf, Ne, ' : ', sorted(indices.tolist()))


def join_completed(list_of_results, key_columns=None):
    completed = [r[r['training_error_simple'] == 0] for r in list_of_results]
    completed = pd.concat(completed, ignore_index=True)
    if key_columns:
        completed.sort(key_columns)
        duplicated = completed.duplicated(key_columns).sum()
        if duplicated > 0:
            msg = 'Duplicate rows: {}'.format(duplicated)
            print(msg, file=stderr)
    return completed


def main():
    parser = argparse.ArgumentParser(
        description='Join results with zero training error.')
    parser.add_argument('-i', type=str, nargs='+', required=True,
                        help='list of input files')
    parser.add_argument('-o', type=str, required=True,
                        help='file to store result')

    args = parser.parse_args()
    completed_df = join_completed([pd.read_json(f) for f in args.files])

    completed_df.to_json(args.outfile)

if __name__ == '__main__':
    main()