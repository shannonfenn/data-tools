import datatools.gen_samples_dichotomous as gen
import numpy as np
import pytest
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'target_matrices')


@pytest.mark.parametrize("opname,Ni,No,Ne", [
    ('add', 4, 1, 8),
    ('sub', 4, 2, 12),
    ('sub', 4, 2, 16),
    ('add', 8, 3, 4),
    ('mul', 8, 3, 64),
    ('and', 8, 4, 128),
    ('mul', 8, 8, 128),
])
def test_single_unique_valid_sample(opname, Ni, No, Ne):
    sample = np.zeros(Ne, dtype=np.uint64)
    op = gen.operator_function(opname, Ni, No)
    gen.single_unique_valid_sample(op, Ni, No, Ne, sample)

    # generate output patterns from sample
    filename = os.path.join(DATA_DIR, '{}{}.npy'.format(opname, Ni))
    full_target = np.load(filename)
    target_matrix = full_target[sample, :No]

    print(target_matrix)

    assert np.all(np.any(target_matrix, axis=0))
    assert not np.any(np.all(target_matrix, axis=0))


@pytest.mark.parametrize("opname,Ni,No,Ne,Ns", [
    ('add', 4, 1, 8, 50),
    ('sub', 4, 2, 12, 50),
    ('sub', 4, 2, 16, 50),
    ('add', 8, 3, 4, 10),
    ('mul', 8, 4, 64, 100),
    ('and', 8, 4, 128, 10),
    ('mul', 8, 8, 128, 150),
])
def test_unique_valid_samples(opname, Ni, No, Ne, Ns):
    op = gen.operator_function(opname, Ni, No)
    samples = gen.unique_valid_samples(op, Ni, No, Ns, Ne)

    # generate output patterns from sample
    filename = os.path.join(DATA_DIR, '{}{}.npy'.format(opname, Ni))
    full_target = np.load(filename)
    target_matrix = full_target[samples][:, :No]

    assert np.all(np.any(target_matrix, axis=2))
    assert not np.any(np.all(target_matrix, axis=2))
