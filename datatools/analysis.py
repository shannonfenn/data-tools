import functools
import numpy as np


def get_Ni(df):
    if df.Ni.min() == df.Ni.max():
        return df.Ni.min()
    else:
        raise ValueError('Non-uniform Ni')


def get_No(df):
    if df.No.min() == df.No.max():
        return df.No.min()
    else:
        raise ValueError('Non-uniform No')


def mean_nonzero(col):
    return np.ma.masked_values(col, 0.0, rtol=0, copy=False).mean()


def accuracy(orders):
    CM = confusion_matrix(orders)
    if CM is None:
        return None
    else:
        return CM.trace() / CM.sum()


def confusion_matrix(orders):
    # if there are None/NaNs in the array then there is no valid CM
    if orders.isnull().values.any():
        return None

    # we want a 2D array from the incoming pandas series of lists
    orders = np.array(orders.tolist())

    num_vals = orders.shape[1]

    # an orders array with values outside [0, num_vals)
    # indicates a pretty big problem
    if orders.max() >= num_vals or orders.min() < 0:
        raise ValueError('Input array has values outside [0, num_vals)')

    CM = np.zeros((num_vals, num_vals), dtype=int)
    for i in range(num_vals):
        indices, counts = np.unique(orders[:, i], return_counts=True)
        CM[i, indices] = counts
    return CM


def confusion_matrix_reducer(orders):
    CM = confusion_matrix(orders)
    if CM is not None:
        CM = CM.tolist()
    return CM


def sampling_settings(df):
    Ni_values = np.unique(df.Ni)
    if len(Ni_values) > 1:
        print('More than one Ni')
        return None

    Ni = Ni_values[0]
    Ne_values = np.unique(df.Ne)
    Ne_seed_pairs = []

    for Ne in Ne_values:
        seeds = np.unique(df[df.Ne == Ne].sample_seed)
        if len(seeds) > 1:
            print('More than one ({}) seed for Ne = {}'.format(
                len(seeds), Ne))
            return None
        Ne_seed_pairs.append((Ne, seeds[0]))

    return Ni, Ne_seed_pairs


def trapz(y, df, x_series):
    x = df.ix[y.index][x_series]
    return np.trapz(y, x=x)


def cumulative_scores(df, by, verbose):
    if isinstance(by, str):
        by = [by]

    for c in by + ['s', 'gen_mean', 'gen_score']:
        if c not in df:
            raise ValueError('Column not in the dataframe: {}'.format(c))

    No = get_No(df)

    trapz_func = functools.partial(trapz, df=df, weight_series='s')

    aggregations = {
        'gen_mean': {'cum_gen_prob': trapz_func},
        'gen_score': {'cum_gen_score': trapz_func},
        'gen_score_nonzero': {'cum_gen_score_nz': trapz_func}
    }
    for i in range(No):
        # Cumulative Generalisation Probability
        src = 'gen_tgt_{}_mean'.format(i)
        dest = 'cgp_t{}'.format(i)
        aggregations[src] = {dest: trapz_func}
        # Cumulative Generalisation Score
        src = 'gen_score_tgt_{}_mean'.format(i)
        dest = 'cgs_t{}'.format(i)
        aggregations[src] = {dest: trapz_func}
        # Cumulative Generalisation Score Ignoring Zeroes
        src = 'gen_score_tgt_{}_nonzero'.format(i)
        dest = 'cgsnz_t{}'.format(i)
        aggregations[src] = {dest: trapz_func}

    return df.groupby(by).agg(aggregations)


def aggregate_runs(raw, key_columns):
    No = get_No(raw)
    for t in range(No):
        target_generalised = raw['test_err_tgt_{}'.format(t)] == 0
        raw['gen_tgt_{}'.format(t)] = target_generalised
        target_memorised = raw['trg_err_tgt_{}'.format(t)] == 0
        raw['mem_tgt_{}'.format(t)] = target_memorised

    raw['gen'] = raw.gen_tgt_0
    raw['mem'] = raw.mem_tgt_0
    for t in range(1, No):
        raw.gen = raw.gen & raw['gen_tgt_{}'.format(t)]
        raw.mem = raw.mem & raw['mem_tgt_{}'.format(t)]

    # check that all configurations have memorised
    if not all(raw['mem']):
        print('Warning: {} configurations have not achieved memorisation!'.
              format(len(raw['mem']) - sum(raw['mem'])))

    grouped = raw.groupby(key_columns)

    # training data
    cols_to_keep = dict()
    cols_to_keep['trg_error'] = [np.mean, np.std, mean_nonzero]
    cols_to_keep['mem'] = np.mean
    cols_to_keep.update(
        {'mem_tgt_{}'.format(t): np.mean for t in range(No)})
    cols_to_keep.update(
        {'trg_err_tgt_{}'.format(t): [np.mean, np.std, mean_nonzero]
         for t in range(No)})
    # test data
    cols_to_keep['test_error'] = [np.mean, np.std, mean_nonzero]
    cols_to_keep['gen'] = np.mean
    cols_to_keep.update(
        {'gen_tgt_{}'.format(t): np.mean for t in range(No)})
    cols_to_keep.update(
        {'test_err_tgt_{}'.format(t): [np.mean, np.std, mean_nonzero]
         for t in range(No)})

    if 'tgt_order' in raw:
        cols_to_keep['tgt_order'] = [confusion_matrix_reducer, accuracy]

    aggregated = grouped.aggregate(cols_to_keep).reset_index()

    # collapse the multi-index columns by concatenating the names
    aggregated.columns = [' '.join(col).strip().replace(' ', '_')
                          for col in aggregated.columns.values]

    # Scores defined by Goudarzi et. al.
    aggregated['trg_score'] = 1 - aggregated.trg_error_mean
    aggregated['gen_score'] = 1 - aggregated.test_error_mean
    for i in range(No):
        src_key = 'trg_err_tgt_{}_mean'.format(i)
        new_key = 'trg_score_tgt_{}'.format(i)
        aggregated[new_key] = 1 - aggregated[src_key]
        src_key = 'test_err_tgt_{}_mean'.format(i)
        new_key = 'gen_score_tgt_{}'.format(i)
        aggregated[new_key] = 1 - aggregated[src_key]

    # scores for non-generalised cases
    aggregated['trg_score_nonzero'] = 1 - aggregated.trg_error_mean_nonzero
    aggregated['gen_score_nonzero'] = 1 - aggregated.test_error_mean_nonzero
    for i in range(No):
        src_key = 'trg_err_tgt_{}_mean_nonzero'.format(i)
        new_key = 'trg_score_tgt_{}_nonzero'.format(i)
        aggregated[new_key] = 1 - aggregated[src_key]
        src_key = 'test_err_tgt_{}_mean_nonzero'.format(i)
        new_key = 'gen_score_tgt_{}_nonzero'.format(i)
        aggregated[new_key] = 1 - aggregated[src_key]

    aggregated['No'] = No

    # record normalised sample size
    Ni = get_Ni(raw)
    aggregated['s'] = aggregated.Ne / 2**Ni
    return aggregated
