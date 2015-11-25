from datatools.gen_samples_dichotomous import unique_valid_samples
from datatools.gen_samples_dichotomous import single_unique_valid_sample
from datatools.gen_samples_dichotomous import OPERATOR_MAP, operator_function
import numpy as np
import pytest


@pytest.fixture(params=OPERATOR_MAP.keys())
def operator_name(request):
    return request.param


@pytest.mark.parametrize("opname,Ni,No,Ne", [
    ('add', 4, 1, 8),
    ('sub', 4, 2, 12),
    ('sub', 4, 2, 16),
    ('add', 8, 3, 4),
    ('mul', 8, 3, 64),
    ('div', 8, 4, 128),
])
def test_single_unique_valid_sample(opname, Ni, No, Ne):
    samples = np.zeros(Ne, dtype=np.uint64)
    op = operator_function(opname, Ni, No)
    single_unique_valid_sample(op, Ni, No, Ne, samples)

    # need to generate output patterns from samples

    assert np.any(samples)
    assert not np.all(samples)


@pytest.mark.parametrize("opname,Ni,No,Ne,Ns", [
    ('add', 4, 1, 8, 50),
    ('sub', 4, 2, 12, 50),
    ('sub', 4, 2, 16, 50),
    ('add', 8, 3, 4, 10),
    ('mul', 8, 4, 64, 100),
    ('div', 8, 8, 128, 150),
])
def test_unique_valid_samples(opname, Ni, No, Ne, Ns):
    op = operator_function(opname, Ni, No)
    samples = unique_valid_samples(op, Ni, No, Ns, Ne)
    assert np.all(np.any(samples, axis=1))
    assert not np.any(np.all(samples, axis=1))
