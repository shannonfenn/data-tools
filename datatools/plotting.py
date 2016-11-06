import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import statsmodels.stats.api as sms


def mean_conf_int(grouped, alpha):
    return grouped.agg({
        'centre': np.mean,
        'lower': lambda x: sms.DescrStatsW(x).tconfint_mean(alpha)[0] - np.mean(x),
        'upper': lambda x: sms.DescrStatsW(x).tconfint_mean(alpha)[1] - np.mean(x)
    })


def plot_with_errs(ax, data, label=None, color=None, marker=None, linestyle=None, err_style=None):
    if err_style == 'band':
        ax = data.centre.plot(ax=ax, label=label, marker=marker, color=color, style=linestyle, mec=color)
        l = data.lower + data.centre
        u = data.upper + data.centre
        ax.fill_between(data.centre.index, l, u, alpha=0.25, linewidth=0, color=color)
    elif err_style == 'bars':
        err = abs(np.vstack((data.lower, data.upper)))
        ax = data.centre.plot(ax=ax, label=label, marker=marker, color=color, yerr=err, style=linestyle, mec=color)
    else:
        ax = data.centre.plot(ax=ax, label=label, marker=marker, color=color, style=linestyle, mec=color)


def filter_rename_groupby(df, by, oldcols, newcols):
    df = df[['s'] + oldcols]
    df = df.rename(columns=dict(zip(oldcols, newcols)))
    return df.groupby('s')


def single_plot(df, cols, colormap, markermap, linestylemap, legendmap={},
                err_style='band', alpha=0.05, axis_modifier=None):
    if not legendmap:
        legendmap = {c: c for c in cols}  # identity dict
    fig, ax = plt.subplots()
    grouped = filter_rename_groupby(df, 's', cols, cols)
    for c in cols:
        data = mean_conf_int(grouped[c], alpha)
        plot_with_errs(ax, data, legendmap[c], colormap[c], markermap[c],
                       linestylemap[c], err_style)
    axis_modifier(ax)
    return fig


def multi_plot(df, targets, basecols, colormap, markermap, linestylemap,
               legendmap={}, err_style='band', alpha=0.05, axis_modifier=None):
    if not legendmap:
        legendmap = {c: c for c in basecols}  # identity dict
    fig, axes = plt.subplots(len(targets), 1, sharex=True, sharey=True)

    for t, ax in zip(targets, axes):
        tgt_cols = ['{} target {}'.format(c, t) for c in basecols]
        grouped = filter_rename_groupby(df, 's', tgt_cols, basecols)
        for c in basecols:
            data = mean_conf_int(grouped[c], alpha)
            plot_with_errs(ax, data, legendmap[c], colormap[c], markermap[c],
                           linestylemap[c], err_style)
        axis_modifier(ax)
    return fig
