import glob
import os.path
import feather
import pandas as pd


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
