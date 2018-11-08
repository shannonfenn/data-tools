import numpy as np
from statsmodels.stats import api as sms
import datatools.ranking as rnk


def percentile(n):
    def percentile_(x):
        return np.percentile(x, q=n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


def conf_l(n):
    def conf_l_(x):
        return sms.DescrStatsW(x).tconfint_mean(1-n/100)[0]
    conf_l_.__name__ = 'conf_l_%s' % n
    return conf_l_


def conf_u(n):
    def conf_u_(x):
        return sms.DescrStatsW(x).tconfint_mean(1-n/100)[1]
    conf_u_.__name__ = 'conf_u_%s' % n
    return conf_u_


def conf_delta(n):
    def conf_delta_(x):
        return 0.5*(sms.DescrStatsW(x).tconfint_mean(1-n/100)[1] -
                    sms.DescrStatsW(x).tconfint_mean(1-n/100)[0])
    conf_delta_.__name__ = 'conf_delta_%s' % n
    return conf_delta_


def overlap(A, B):
    A, B = set(A), set(B)
    if len(A) == 0 or len(B) == 0:
        return 0
    return len(A & B) / min(len(A), len(B))


def nestedness(F):
    # F is assumed to be ordered
    return np.mean([overlap(f1, f2) for f1, f2 in zip(F[:-1], F[1:])])


def cardinality_rank(cardinalities, break_ties=False):
    return rnk.cost_rank(cardinalities, break_ties)


def generalisation_frequency(mccs):
    return sum(mccs == 1) / len(mccs)
