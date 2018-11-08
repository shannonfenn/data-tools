import numpy as np
import pandas as pd
import functools
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import datatools.measures as measures


# Plot elements
TEST_MCC_LABEL = 'Test MCC'
TEST_MACRO_MCC_LABEL = 'Test Macro-MCC'
TEST_CUM_MACRO_MCC_LABEL = 'Cumulative Macro-MCC (test)'
TRG_TIME_LABEL = 'Training Time (s)'
TAU_LABEL = r'Cumulative Rank Correlation ($\tau$)'
TARGET_LABEL = 'Target'
NE_LABEL = 'Training Set Size'
GEN_FREQ_LABEL = 'Generalisation Frequency'
METRIC_LABELS = {
    'test_mcc': TEST_MACRO_MCC_LABEL,
    'time_learning': TRG_TIME_LABEL,
    'tau': TAU_LABEL,
}


def set_common_params():
    plt.rcParams.update({
       'axes.labelsize': 11,
       'font.size': 12,
       'legend.fontsize': 11,
       'xtick.labelsize': 10,
       'ytick.labelsize': 10
       })
    plt.rc('text', usetex=False)
    plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Arial']})
    # plt.rc('text', usetex=True)
    # plt.rc('font', **{'family': 'serif', 'serif': ['Helvetica']})
    mpl.rcParams['figure.dpi'] = 600
    mpl.rcParams['savefig.dpi'] = 600
    mpl.rcParams['legend.frameon'] = False


def plt_mcc_time_vs_ne_all_datasets(df, sharex=False, sharey=False):
    g = _plt_multiple_metrics_vs_ne_all_datasets(
        df,
        metrics_map={m: METRIC_LABELS[m]
                     for m in ['test_mcc', 'time_learning']},
        sharex=sharex, sharey=sharey)
    g.set_ylabels('')
    return g


def plt_mcc_time_vs_ne_single_dataset(df, dataset, col_wrap=None, sharey=False):
    g = _plt_multiple_metrics_vs_ne_single_dataset(
        df, dataset,
        metrics_map={m: METRIC_LABELS[m]
                     for m in ['test_mcc', 'time_learning']},
        col_wrap=col_wrap,
        sharey=sharey)
    g.set_ylabels('')
    return g


def plt_mcc_tau_time_vs_ne_single_dataset(df, dataset, col_wrap=None, sharey=False):
    g = _plt_multiple_metrics_vs_ne_single_dataset(
        df, dataset,
        metrics_map={m: METRIC_LABELS[m]
                     for m in ['test_mcc', 'tau', 'time_learning']},
        col_wrap=col_wrap,
        sharey=sharey)
    g.set_ylabels('')
    return g


def plt_mcc_tgt_by_dataset(df, sharex=False, sharey=False):
    g = _plt_multiple_metrics_vs_ne_all_datasets(
        df,
        metrics_map={f'test_mcc_tgt_{t}': f'Target: {t}'
                     for t in list(range(df.No.max()))},
        sharex=sharex, sharey=sharey)
    g.set_ylabels(TEST_MACRO_MCC_LABEL)
    return g


def plt_cum_mcc(df, normalise=False, errors=True, ax=None, plot_kwargs={}):
    ax = _plot_cumulative_vs_dataset(df, 'test_mcc', normalise, errors, ax=ax, plot_kwargs=plot_kwargs)
    ax.set_xlabel('')
    ax.set_ylabel(TEST_CUM_MACRO_MCC_LABEL)
    ax.set_ylim(0, 1)
    return ax


def plt_cum_tau(df, normalise=False, errors=True, ax=None, plot_kwargs={}):
    ax = _plot_cumulative_vs_dataset(df, 'tau', normalise, errors,
                                     legend_title='Curriculum', ax=ax,
                                     plot_kwargs=plot_kwargs)
    ax.set_xlabel('')
    ax.set_ylabel(TAU_LABEL)
    # ax.set_ylim(0, 1)
    return ax


def plt_cum_time(df, column, label, normalise=False, errors=True, logy=True, ax=None, plot_kwargs={}):
    ax = _plot_cumulative_vs_dataset(df, column, normalise, errors, logy, ax=ax, plot_kwargs=plot_kwargs)
    ax.set_xlabel('')
    ax.set_ylabel(label)
    ax.xaxis.grid(False)
    return ax


def plt_single_metric_vs_ne_single_dataset(df, dataset, metric,
                                           logy=False):
    ax = _plt_single_metric_vs_ne_single_dataset(
        df, dataset, metric, logy)
    ax.set_ylabel(METRIC_LABELS[metric])
    return ax.get_figure()


def plt_single_metric_vs_ne_multiple_datasets(df, metric, logy=False, col_wrap=None):
    g = _plt_single_metric_vs_ne_multiple_datasets(
        df, metric, logy, col_wrap)
    g.set_ylabels(METRIC_LABELS[metric])
    return g


def _plt_single_metric_vs_ne_single_dataset(
        df, dataset, metric, logy, legend_title='', ci=95):
    ax = sns.lineplot(x='Ne', y=metric, data=df[df.dataset == dataset],
                      ci=ci, hue='treatment', style='treatment')

    ax.get_legend().texts[0].set_text(legend_title)
    ax.set_xlabel(NE_LABEL)
    if logy:
        ax.set_yscale('log')
    sns.despine()

    return ax


def _plt_single_metric_vs_ne_multiple_datasets(
        df, metric, logy, col_wrap, legend_title='', ci=95):
    g = sns.relplot(
        kind='line', x='Ne', y=metric, hue='treatment', style='treatment',
        data=df, col='dataset', col_wrap=col_wrap, ci=ci, height=4,
        facet_kws={'sharex': True, 'sharey': True})
    g.set_titles(col_template='{col_name}')
    g._legend.texts[0].set_text(legend_title)
    g.set_xlabels(NE_LABEL)
    return g


def _plt_multiple_metrics_vs_ne_single_dataset(
        df, dataset, metrics_map, col_wrap, sharey, legend_title='', ci=95):

    df_long = pd.melt(df[df.dataset == dataset],
                      id_vars=['treatment', 'Ne'],
                      value_vars=metrics_map.keys())
    df_long.variable = df_long.variable.replace(metrics_map)
    # plot
    g = sns.relplot(
        kind='line', x='Ne', y='value', hue='treatment', style='treatment',
        data=df_long, col='variable', col_wrap=col_wrap, ci=ci, height=4,
        facet_kws={'sharex': True, 'sharey': sharey})
    g.set_titles(col_template='{col_name}')
    g._legend.texts[0].set_text(legend_title)
    g.set_xlabels(NE_LABEL)
    return g


def _plt_multiple_metrics_vs_ne_all_datasets(
        df, metrics_map, sharex, sharey, legend_title='', ci=95):
    df_long = pd.melt(df,
                      id_vars=['dataset', 'treatment', 'Ne'],
                      value_vars=metrics_map.keys())
    df_long.variable = df_long.variable.replace(metrics_map)
    # plot
    g = sns.relplot(
        kind='line', x='Ne', y='value', hue='treatment', style='treatment',
        data=df_long, row='dataset', col='variable', ci=ci, height=4,
        facet_kws={'margin_titles': True, 'sharex': sharex, 'sharey': sharey})
    for ax in g.axes.flat:
        # remove original texts before set_titles()
        # since margin title implementation is hacky
        plt.setp(ax.texts, text='')
    g.set_titles(row_template='{row_name}', col_template='{col_name}')
    g._legend.texts[0].set_text(legend_title)
    g.set_xlabels(NE_LABEL)
    return g


def _plot_cumulative_vs_dataset(df, value, normalise=False, errors=True,
                                logy=False, legend_title='', ax=None, plot_kwargs={}):
    ax = _cumul_plot(df, value, errors, logy, ax=ax, plot_kwargs=plot_kwargs)
    ax.legend(title=legend_title, loc='center left', bbox_to_anchor=(1, 0.5))
    return ax


def _cumul_plot(df, value, errors, logy=False, ax=None, normalise=False, plot_kwargs={}):
    statistics = {'error': measures.conf_delta(95),
                  'center': np.mean}
    grp = df.groupby(['dataset', 'treatment', 'Ne'])[value]
    grp = grp.agg(statistics.values()).reset_index()
    grp = grp.rename(columns={func.__name__: new_name
                              for new_name, func in statistics.items()})

    cumulative = functools.partial(measures.norm_trapz, df=grp, x_series='Ne')
    grp = grp.groupby(['dataset', 'treatment'])
    summary = grp.agg(cumulative)
    if normalise:
        summary = summary.groupby(level=[0, 1]).transform(lambda x: x/x.max())

    yerr = summary['error'].unstack() if errors else None
    ax = summary['center'].unstack().plot(ax=ax, kind='bar', yerr=yerr,
                                          logy=logy, legend=False, **plot_kwargs)
    sns.despine()

    return ax


# def plt_cumulative_single_dataset(df, dataset, value, normalise=False,
#                                   errors=True, logy=False, legend_title=''):
#     statistics = {
#         'error': conf_delta(95),
#         'center': np.mean
#     }

#     grp = df[df.dataset == dataset].groupby(['treatment', 'Ne'])[value]
#     grp = grp.agg(statistics.values()).reset_index()
#     grp = grp.rename(columns={func.__name__: new_name
#                               for new_name, func in statistics.items()})

#     cumulative = functools.partial(norm_trapz, df=grp, x_series='Ne')
#     grp = grp.groupby('treatment')
#     summary = grp.agg(cumulative)
#     if normalise:
#         summary = summary.groupby(level=[0, 1]).transform(lambda x: x/x.max())

#     yerr = summary[['error']].transpose() if errors else None

#     ax = summary[['center']].transpose().plot(kind='bar', yerr=yerr, logy=logy)

#     sns.despine()

#     return ax.get_figure()


def plt_cum_mcc_vs_tgt(df, normalise=False):
    statistics = {
        'error': measures.conf_delta(95),
        'center': np.mean
    }

    basecol = 'test_mcc'
    target_names = [str(i) for i in range(df.No.max())]
    value_vars = [f'{basecol}_tgt_{t}' for t in target_names]
    df_long = pd.melt(df, id_vars=['dataset', 'treatment', 'Ne'],
                      value_vars=value_vars)

    grp = df_long.groupby(['dataset', 'treatment', 'Ne', 'variable'])
    grp = grp['value'].agg(statistics.values()).reset_index()
    grp = grp.rename(columns={func.__name__: new_name
                              for new_name, func in statistics.items()})
    grp['target'] = grp['variable'].replace(r'^test_mcc_tgt_(.*)$', r'\1',
                                            regex=True)
    grp.target = grp.target.astype(int)

    cumulative = functools.partial(measures.norm_trapz, df=grp, x_series='Ne')
    g2 = grp.groupby(['target', 'dataset', 'treatment'])
    summary = g2.agg(cumulative)
    if normalise:
        summary = summary.groupby(level=[0, 1]).transform(lambda x: x/x.min())
    summary.reset_index(inplace=True)

    g = sns.FacetGrid(summary, col='dataset', hue='treatment', col_wrap=2,
                      height=3, sharex=True, sharey=True, margin_titles=True)
    g = g.map(plt.plot, 'target', 'center').set_titles('{col_name}')
    g.add_legend(title='')
    g.set_xlabels(TARGET_LABEL)
    g.set_ylabels(TEST_MCC_LABEL)

    return g


def plt_gen_freq(df):
    values = ['test_mcc']
    df_long = pd.melt(df, id_vars=['dataset', 'treatment', 'Ne'],
                      value_vars=values)

    grp = df_long.groupby(['dataset', 'treatment', 'Ne', 'variable'])
    grp = grp['value'].agg([measures.generalisation_frequency]).reset_index()

    g = sns.FacetGrid(grp, col='dataset', hue='treatment', col_wrap=3,
                      height=3, sharex=False, sharey=True, margin_titles=True,
                      ylim=(0, 1))
    g = g.map(plt.plot, 'Ne', 'generalisation_frequency')
    g.add_legend(title='')
    g.set_titles('{col_name}')
    g.set_ylabels(GEN_FREQ_LABEL)

    return g
