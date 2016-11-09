import numpy as np
import matplotlib.pyplot as plt


def plot_with_errs(ax, data, centre, lower=None, upper=None, label=None,
                   color=None, marker=None, linestyle=None, err_style=None):
    if err_style == 'band':
        ax = data[centre].plot(ax=ax, label=label, marker=marker, color=color, style=linestyle, mec=color)
        l = data[centre] - data[lower]
        u = data[centre] + data[upper]
        ax.fill_between(data[centre].index, l, u, alpha=0.25, linewidth=0, color=color)
    elif err_style == 'bars':
        err = abs(np.vstack((data[lower], data[upper])))
        ax = data[centre].plot(ax=ax, label=label, marker=marker, color=color, yerr=err, style=linestyle, mec=color)
    else:
        ax = data[centre].plot(ax=ax, label=label, marker=marker, color=color, style=linestyle, mec=color)


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
        axis_modifier(ax)
