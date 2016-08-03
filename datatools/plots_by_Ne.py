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


def generalisation_probability_plots(df, by, independant_var):
    No = get_No(df)

    if independant_var not in ['s', 'Ne']:
        raise ValueError('independant_var must be one of {\'s\', \'Ne\'}')

    # P(Gen) plots
    plot_settings = {
        'gen_tgt_{}_mean'.format(i): {
            'aes': gg.aes(x=independant_var, y='gen_tgt_{}_mean'.format(i),
                          colour=by),
            'labs': gg.labs(y='P(Gen)', title='Probability of generalising'
                                              ' target {}'.format(i))
        }
        for i in range(No)
    }

    plot_settings['gen_mean'] = {
        'aes': gg.aes(x=independant_var, y='gen_mean', colour=by),
        'labs': gg.labs(y='P(Gen)', title='Probability of generalising'
                                          ' all targets')}

    # Mean gen error plots
    plot_settings.update({
        'test_err_tgt_{}_mean'.format(i): {
            'aes': gg.aes(x=independant_var,
                          y='test_err_tgt_{}_mean'.format(i),
                          colour=by),
            'labs': gg.labs(y='Error', title='Mean test error in'
                                             ' target {}'.format(i))
        }
        for i in range(No)
    })

    plot_settings['test_error_mean'] = {
        'aes': gg.aes(x=independant_var, y='test_error_mean', colour=by),
        'labs': gg.labs(y='Error', title='Mean test error.')}

    # training plots
    plot_settings['mem_mean'] = {
        'aes': gg.aes(x=independant_var, y='mem_mean', colour=by),
        'labs': gg.labs(y='P(Mem)', title='Frequency of memorising'
                                          ' all targets')}

    plot_settings['trg_error_mean'] = {
        'aes': gg.aes(x=independant_var, y='trg_error_mean', colour=by),
        'labs': gg.labs(y='Error', title='Mean training error.')}

    plot_settings['trg_score'] = {
        'aes': gg.aes(x=independant_var, y='trg_score', colour=by),
        'labs': gg.labs(y='Score', title='Training score.')}

    plot_settings['gen_score'] = {
        'aes': gg.aes(x=independant_var, y='gen_score', colour=by),
        'labs': gg.labs(y='Score', title='Generalisation score.')}

    # if 'target_order_accuracy' in df:
    #     plot_settings['target_order_accuracy'] = {
    #         'aes': gg.aes(x=independant_var, y='target_order_accuracy',
    #                       colour=by),
    #         'labs': gg.labs(y='Accuracy', title='Target ordering accuracy.')}
    # else:
    #     print('\'target_order_accuracy\' not in dataframe. No plot generated.')

    check_columns_in_dataframe(df, plot_settings.keys())

    plots = {
        colname: gg.ggplot(settings['aes'], df) +
        settings['labs'] + gg.geom_line()
        for colname, settings in plot_settings.items()
    }

    return plots


def main():
    gf_map = {'e1': 'unmodified', 'e2L': 'weighted',
              'e3L': 'local hierarchical', 'e6L': 'global hierarchical'}

    # scores: generalisation probability and mean generalisation error
    default_by = 'guiding function'
    parser = argparse.ArgumentParser(
        description='Calculate generalisation measures for each combination.')
    parser.add_argument('file', type=str)
    parser.add_argument('--outfile-prefix', '-o', type=str)
    parser.add_argument('--by', '-b', type=str, nargs='+',
                        default=default_by)
    parser.add_argument('--independant-var', '-i', type=str,
                        default='s')

    args = parser.parse_args()

    df = pd.read_json(args.file)

    check_columns_in_dataframe(df, ['guiding_function'])

    df['guiding function'].replace(gf_map, inplace=True)

    if args.outfile_prefix:
        prefix = args.outfile_prefix
    else:
        prefix = os.path.dirname(args.file)

    plots = generalisation_probability_plots(df, args.by, args.independant_var)

    for name, plot in plots.items():
        gg.ggsave(plot, prefix + name + '.svg')

if __name__ == '__main__':
    main()
