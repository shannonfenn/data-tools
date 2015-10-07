import numpy as np
import pandas as pd
import ggplot as gg
import argparse
import os


def get_No(data):
    if data.No.min() == data.No.max():
        return data.No.min()
    else:
        raise ValueError('Non-uniform No')


def check_columns_in_dataframe(df, cols):
    for c in cols:
        if c not in df:
            raise ValueError('Column not in the dataframe: {}'.format(c))


def generalisation_probability_plots(df, independant_var):
    No = get_No(df)

    dependent_vars = ['gen_mean'] + ['gen_tgt_{}_mean'.format(i)
                                     for i in range(No)]

    check_columns_in_dataframe(df, dependent_vars + [independant_var])

    plots = {
        dep: gg.ggplot(gg.aes(x='Ne', y=dep, colour=independant_var), df) +
        gg.ylab('P(Gen)') +
        gg.geom_line()
        for dep in dependent_vars}

    return plots


def main():
    gf_map = {'e1': 'unmodified', 'e2L': 'weighted',
              'e3L': 'local hierarchical', 'e6L': 'global hierarchical'}

    # scores: generalisation probability and mean generalisation error
    default_ind_var = 'guiding function'
    parser = argparse.ArgumentParser(
        description='Calculate generalisation measures for each combination.')
    parser.add_argument('file', type=str)
    parser.add_argument('--outfile_prefix', '-o', type=str)
    parser.add_argument('--independant-var', '-i', type=str, nargs='+',
                        default=default_ind_var)

    args = parser.parse_args()

    df = pd.read_json(args.file)

    check_columns_in_dataframe(df, ['optimiser_guiding_function'])

    df['guiding function'] = df.optimiser_guiding_function
    df['guiding function'].replace(gf_map, inplace=True)

    if args.outfile_prefix:
        prefix = args.outfile_prefix
    else:
        prefix = os.path.dirname(args.file)

    plots = generalisation_probability_plots(df, args.independant_var)

    for name, plot in plots.items():
        gg.ggsave(plot, prefix + name + '.svg')

if __name__ == '__main__':
    main()
