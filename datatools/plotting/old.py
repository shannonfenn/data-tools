import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_with_errs(ax, data, centre, lower=None, upper=None, label=None,
                   color=None, marker=None, linestyle=None, err_style=None):
    if err_style == 'band':
        ax = data[centre].plot(ax=ax, label=label, marker=marker, color=color, ls=linestyle, mec=color)
        l = data[centre] - data[lower]
        u = data[centre] + data[upper]
        ax.fill_between(data[centre].index, l, u, alpha=0.25, linewidth=0, color=color)
    elif err_style == 'bars':
        err = abs(np.vstack((data[lower], data[upper])))
        ax = data[centre].plot(ax=ax, label=label, marker=marker, color=color, ls=linestyle, yerr=[err], mec=color)
    else:
        ax = data[centre].plot(ax=ax, label=label, marker=marker, color=color, ls=linestyle, mec=color)


def filter_rename(df, oldcols, newcols):
    df = df[oldcols]
    return df.rename(columns=dict(zip(oldcols, newcols)))


def single_plot(ax, df, cols, centre, lower, upper, colormap,
                markermap, linestylemap, legendmap={}, err_style='band',
                axis_modifier=None):
    if not legendmap:
        legendmap = {c: c for c in cols}  # identity dict
    for c in cols:
        plot_with_errs(ax, df[c], centre, lower, upper, legendmap[c],
                       colormap[c], markermap[c], linestylemap[c], err_style)
    if axis_modifier:
        axis_modifier(ax)


def multi_plot(axes, df, basecols, targets, centre, lower, upper, colormap,
               markermap, linestylemap, legendmap={}, err_style='band',
               axis_modifier=None):
    if not legendmap:
        legendmap = {c: c for c in basecols}  # identity dict

    for t, ax in zip(targets, axes):
        tgt_cols = ['{} target {}'.format(c, t) for c in basecols]
        data = filter_rename(df, tgt_cols, basecols)
        for c in basecols:
            plot_with_errs(ax, data[c], centre, lower, upper, legendmap[c],
                           colormap[c], markermap[c], linestylemap[c],
                           err_style)
        if axis_modifier:
            axis_modifier(ax)


def multi_tgt_plot(df, base_col, target_names, treatment_cols,
                   plot_func=plt.plot, agg_func=np.mean,
                   facet_kwargs={}, plot_kwargs={}):
    value_vars = [base_col] + [base_col+'_{}'.format(t) for t in target_names]

    df_long = pd.melt(df, id_vars=['Ne'] + treatment_cols,
                      value_vars=value_vars)

    df_long.replace([r'^'+base_col+r'$', r'^'+base_col+r'_(.*)$'],
                    [r'overall', r'\1'], regex=True, inplace=True)

    df_long['treatment'] = list(zip(*[df_long[tr] for tr in treatment_cols]))

    df_long['treatment'] = df_long['treatment'].apply(str)
    df_long.rename(columns={'variable': 'target', 'value': base_col},
                   inplace=True)

    grp = df_long.groupby(['Ne', 'treatment', 'target'], as_index=False)
    grp = grp.agg(agg_func)

    g = sns.FacetGrid(grp, col='target', hue='treatment', **facet_kwargs)
    g.map(plot_func, 'Ne', base_col, **plot_kwargs)
    g.add_legend()

    return g
