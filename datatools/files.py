import glob
import os.path
import feather
import pandas as pd
from natsort import natsorted


# Boolean Network Constants
BN_TREATMENTS = ['strat-raps-reduced', 'mono-e6-auto', 'split-cplex', 'cc-auto']
BN_TREATMENT_MAP = {
    # 'strat-raps-reduced':  'IFF',
    # 'mono-e1':             'Monolithic ($L_1$)',
    # 'mono-e6-auto':        'Monolithic ($L_{gh}$)',
    # 'split-cplex':         'IC (w/ feature selection)',
    # 'strat-cplex-reduced': 'Stratified / Optimal',
    # 'cc-auto':             'CC (w/ curriculum)',
    # 'cc-random':           'CC (random)',
    'strat-raps-reduced':  'IFF',
    'mono-e6-auto':        'Monolithic',
    'split-cplex':         'IC',
    'cc-auto':             'CC',
}

BN_NON_ORDERED_TREATMENTS = [
    BN_TREATMENT_MAP[k]
    for k in ['mono-e1', 'split-cplex', 'split-raps', 'cc-random']
    if k in BN_TREATMENT_MAP]

BN_APRIORI_TREATMENTS = [
    BN_TREATMENT_MAP[k]
    for k in ['mono-e2-auto', 'mono-e3-auto', 'mono-e6-auto', 'cc-auto']
    if k in BN_TREATMENT_MAP]

# Neural Network Constants
NN_TREATMENTS = ['layered', 'parallel', 'shared_a', 'shared_b', 'shared_c']
NN_TREATMENT_MAP = {
    'layered':  'IFF',
    'parallel': 'IC',
    'shared_a': 'Wide',
    'shared_b': 'Deep',
    'shared_c': 'Dovetailed',
}

NN_NON_ORDERED_TREATMENTS = [
    NN_TREATMENT_MAP[k]
    for k in ['parallel', 'shared_a', 'shared_b']
    if k in NN_TREATMENT_MAP]

NN_APRIORI_TREATMENTS = [
    NN_TREATMENT_MAP[k]
    for k in ['shared_c']
    if k in NN_TREATMENT_MAP]
A_PRIORI_TMT_NAME = 'a priori'

DATASET_NAME_MAP = {
    'cmaj9': '9-bit cascaded majority',
    'cmux15': '15-bit cascaded multiplexer',
    'cpar7': '7-bit cascaded parity',
    }
for i in [3, 4, 5, 6, 7, 8, 16, 32, 48, 64, 96, 128]:
    DATASET_NAME_MAP[f'add{i}'] = f'{i}-bit'
for i, c in zip(range(10), 'ABCDEFGHIJ'):
    DATASET_NAME_MAP[f'gen{i}'] = f'{c}'


def update_names(df, treatment_map=BN_TREATMENT_MAP, treatments=BN_TREATMENTS):
    treatments = df.treatment.cat.categories.intersection(treatments)
    df.dataset.cat.rename_categories(DATASET_NAME_MAP, inplace=True)
    df.dataset.cat.reorder_categories(natsorted(df.dataset.cat.categories),
                                      ordered=True, inplace=True)
    df = df[df.treatment.isin(treatments)]
    df.treatment.cat.rename_categories(treatment_map, inplace=True)
    df.treatment.cat.remove_unused_categories(inplace=True)
    df.treatment.cat.reorder_categories([treatment_map[k] for k in treatments],
                                        ordered=True, inplace=True)
    return df


def convert_treatment_to_curricula(df, non_ordered, apriori):
    df = df[~(df.treatment.isin(non_ordered))].copy()
    df.treatment.cat.add_categories(['a priori'], inplace=True)
    df.treatment[df.treatment.isin(apriori)] = A_PRIORI_TMT_NAME
    df.treatment.cat.remove_unused_categories(inplace=True)
    return df


def load_results(directory, remove_failed=False):
    directory = os.path.expanduser(directory)
    if os.path.exists(os.path.join(directory, 'results.feather')):
        return _load_single_results(directory, remove_failed)
    else:
        subdirs = glob.glob(os.path.join(directory, '*/'))
        return _load_results_from_subdirs(subdirs, remove_failed)


def load_multiple_results(directories, remove_failed=False):
    subdirs = []
    for d in directories:
        d = os.path.expanduser(d)
        if os.path.exists(os.path.join(d, 'results.feather')):
            subdirs.append(d)
        else:
            subdirs.extend(glob.glob(os.path.join(d, '*/')))
    return _load_results_from_subdirs(subdirs, remove_failed)


def _load_results_from_subdirs(subdirs, remove_failed):
    dfs = []
    for subdir in subdirs:
        df = _load_single_results(subdir, remove_failed)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True, sort=True)
    df.dataset = df.dataset.astype('category')
    df.treatment = df.treatment.astype('category')
    return df


def _load_single_results(directory, remove_failed):
    df = feather.read_dataframe(os.path.join(directory, 'results.feather'))
    num_failed = sum(df.trg_err > 0)
    msg = f'{os.path.basename(os.path.normpath(directory))}: {num_failed} of {len(df)} failed'
    if num_failed > 0:
        if remove_failed:
            msg += ' [removed].'
            df = df[df.trg_err == 0]
        else:
            msg += ' [kept].'
    print(msg)
    return df
