import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import statsmodels.stats.api as sms


def plot_with_conf_int(grouped, cols, colormap, labelmap, show_confs=True,
                       alpha=0.05, agg_func=np.mean, axis_modifier=None,
                       outfilename=None):
    # set the ordering to that given by cols
    agged = grouped.agg({col: np.mean for col in cols})[cols]
    if labelmap:
        labels = [labelmap[col] for col in cols]
        agged = agged.rename(columns={c: l for c, l in zip(cols, labels)})

    mpl_colormap = mpl.colors.ListedColormap([colormap[col] for col in cols])

    ax = agged.plot(marker='.', colormap=mpl_colormap)
    if show_confs:
        conf_lower = grouped.agg({col: lambda x: sms.DescrStatsW(x).tconfint_mean(alpha)[0] for col in cols})
        conf_upper = grouped.agg({col: lambda x: sms.DescrStatsW(x).tconfint_mean(alpha)[1] for col in cols})
        for col in cols:
            ax.fill_between(conf_lower.index, conf_lower[col], conf_upper[col],
                            alpha=0.25, linewidth=0, color=colormap[col])

    if axis_modifier is not None:
        axis_modifier(ax)

    if outfilename is not None:
        plt.savefig(outfilename, format='pdf', dpi=1200)

    return ax


def multi_plot(df, No, cols, colormap, labelmap={}, save=False, file_prefix='',
               axis_modifier=None):
    grouped = df.groupby('s')
    axes = []
    if not labelmap:
        labelmap = {c: c for c in cols}  # identity dict

    # group by Ne and get the mean error difference
    fname = '{}_all_tgts.pdf'.format(file_prefix) if save else None
    ax = plot_with_conf_int(grouped, cols, colormap, labelmap, show_confs=True,
                            alpha=0.05, axis_modifier=axis_modifier,
                            outfilename=fname)
    axes.append(ax)

    for t in range(No):
        fname = '{}_t{}.pdf'.format(file_prefix, t) if save else None
        subcols = ['{} target {}'.format(c, t) for c in cols]
        cm = {'{} target {}'.format(c, t): colormap[c] for c in cols}
        lm = {'{} target {}'.format(c, t): labelmap[c] for c in cols}
        ax = plot_with_conf_int(grouped, subcols, cm, lm, show_confs=True,
                                alpha=0.05, axis_modifier=axis_modifier,
                                outfilename=fname)
        axes.append(ax)
    return axes
