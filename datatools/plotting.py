import numpy as np
import datatools.analysis as ana
import matplotlib as mpl
import matplotlib.pyplot as plt
import statsmodels.stats.api as sms


def plot_with_conf_int(grouped, cols, colormap, show_confs=True, alpha=0.05,
                       labels=[], agg_func=np.mean, xlab='', ylab='', title='',
                       axis_modifier=None, outfilename=None):
    # set the ordering to that given by cols
    agged = grouped.agg({col: np.mean for col in cols})[cols]
    if labels:
        agged = agged.rename(columns={c: l for c, l in zip(cols, labels)})

    mpl_colormap = mpl.colors.ListedColormap([colormap[col] for col in cols])

    ax = agged.plot(marker='.', colormap=mpl_colormap)
    if show_confs:
        conf_lower = grouped.agg({col: lambda x: sms.DescrStatsW(x).tconfint_mean(alpha)[0] for col in cols})
        conf_upper = grouped.agg({col: lambda x: sms.DescrStatsW(x).tconfint_mean(alpha)[1] for col in cols})
        for col in cols:
            ax.fill_between(conf_lower.index, conf_lower[col], conf_upper[col],
                            alpha=0.25, linewidth=0, color=colormap[col])

    if title:
        ax.set_title(title)
    if xlab:
        ax.set_xlabel(xlab)
    if ylab:
        ax.set_ylabel(ylab)

    if axis_modifier is not None:
        axis_modifier(ax)

    if outfilename is not None:
        plt.savefig(outfilename, format='pdf', dpi=1200)

    return ax


def plot_diffs(df, cols, colormap, save=False, file_prefix=''):
    def axis_modifier(ax):
        ax.hlines([0], *ax.get_xlim(), linestyles='dotted')

    grouped = df.groupby('s')
    smin, smax = df.s.min(), df.s.max()
    axes = []
    # group by Ne and get the mean error difference
    fname = '{}_all_tgts.pdf'.format(file_prefix) if save else None
    
    ax = plot_with_conf_int(grouped, cols, colormap, show_confs=True,
                            alpha=0.05, xlab='Sample fraction ($s$)',
                            ylab='$\Delta Accuracy$',
                            axis_modifier=axis_modifier,
                            outfilename=fname)

    
    axes.append(ax)

    if save:
        plt.savefig(, format='pdf', dpi=1200)

    for t in range(ana.get_No(df)):
        subcols = ['{} target {}'.format(c, t) for c in cols]
        cm = {'{} target {}'.format(c, t): colormap[c] for c in cols}
        ax = plot_with_conf_int(grouped, subcols, cm, show_confs=True,
                                alpha=0.05, labels=cols,
                                xlab='Sample fraction ($s$)',
                                ylab='$\Delta Accuracy$')
        ax.hlines([0], *ax.get_xlim(), linestyles='dotted')
#         ax.set_title('Target {}'.format(t))
        ax.set_ylabel()
        ax.set_xlabel()
        axes.append(ax)

        '{}_tgt_{}.pdf'.format(file_prefix, t)
        
    return axes


def plot_accs(df, cols, colormap, save=False, file_prefix='', xlab=):
    def axis_modifier(ax):
        ax.set_xlim(left=0)
        ax.set_ylim(top=1.005)
        ax.legend(loc='lower right')

    # aggregate mean accuracy
    grouped = df.groupby('s')

    ax = plot_with_conf_int(grouped, cols, colormap, show_confs=True,
                            alpha=0.05, xlab='Sample fraction ($s$)',
                            ylab='Accuracy', axis_modifier=axis_modifier)


    for ax in axes:

    if save:
        filenames = [] + [
        '{}_tgt_{}.pdf'.format(file_prefix, t) for t in range(ana.get_No(df))]

        plt.savefig(, format='pdf', dpi=1200)

    for t in range(ana.get_No(df)):
        subcols = ['{} target {}'.format(c, t) for c in cols]
        cm = {'{} target {}'.format(c, t): colormap[c] for c in cols}
        ax = plot_with_conf_int(grouped, subcols, cm, show_confs=True,
                                alpha=0.05, labels=cols,
                                xlab='Sample fraction ($s$)', ylab='Accuracy')
        ax.set_xlim(left=0)
        ax.set_ylim(top=1.005)
        ax.legend(loc='lower right')
        if save:
            plt.savefig('{}_tgt_{}.pdf'.format(file_prefix, t), format='pdf', dpi=1200)
