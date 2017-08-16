import datatools.utils as utils
import numpy as np
import pytest
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'instances')


@pytest.mark.parametrize("seed,expected", [
    (2096902292, [[11, 44, 66, 78, 84], [20, 31, 60, 70], [5, 54, 72], [24, 82, 89], [3, 58], [27, 46, 53, 73], [12, 13, 33, 56, 59, 85, 87], [6, 8, 19, 43, 99], [18, 95], [0, 36, 51, 52, 71], [25, 49, 90], [42, 64], [68, 74, 75], [63, 92], [4, 57], [1, 26, 39, 41], [30, 34, 38, 62, 65, 69, 93, 96], [45, 80], [7, 76, 77, 88], [14, 81], [9, 37], [15, 21, 32, 55, 61, 83, 86, 94, 98], [2, 22, 28], [10, 29, 47, 48, 50, 67], [35, 97]]),
    (1679947158, [[22, 47], [3, 48, 85], [37, 58, 93], [31, 40, 55, 79, 80, 89, 91, 97], [21, 39, 45, 62, 68], [4, 30], [53, 57], [11, 74, 95], [13, 15, 28, 88], [26, 75, 90], [5, 20, 23, 33, 36, 78, 86], [24, 43, 71, 72], [8, 27, 50], [46, 52, 60, 82], [19, 42], [6, 38, 44, 94], [10, 25, 49, 54], [7, 56], [12, 34], [32, 61, 66], [17, 64], [16, 67, 87, 92, 99], [2, 73, 98], [0, 65, 69], [81, 83, 96], [9, 18, 29, 63], [1, 35, 59, 70, 76, 77]]),
    (1655332568, [[12, 13, 36, 39, 60], [41, 59], [6, 69], [24, 80, 82], [18, 85, 88, 89], [14, 45, 72, 95], [57, 92], [28, 34, 38, 50, 98], [26, 31], [5, 78, 96], [29, 42, 87, 99], [4, 64], [1, 17, 30, 33, 47, 66], [46, 53, 73, 86, 91], [19, 49], [8, 9, 37, 61, 63], [43, 79, 81, 90], [3, 51, 93], [0, 23, 25, 27, 68], [56, 74], [10, 75], [35, 48, 71, 97], [32, 76], [16, 21, 40, 44, 52, 58, 70], [7, 83], [15, 22], [11, 54, 65], [20, 62], [67, 77, 84, 94]]),
])
def test_duplicate_patterns(seed, expected):
    np.random.seed(seed)
    X = np.random.randint(2, size=(100, 5), dtype=np.uint8)

    assert utils.duplicate_patterns(X) == expected


@pytest.mark.parametrize("seed,expected", [
    (2919627149, [1, 9, 0, 2, 6, 10, 13, 3, 7, 5, 19, 4, 22]),
    (1033918002, [1, 19, 11, 13, 6, 12, 16, 22, 15, 18]),
    (4129451494, [19, 22, 11, 17, 5, 9, 10, 4, 12, 14, 16, 0, 7, 18, 20, 6, 24]),
])
def test_duplicate_patterns_flat(seed, expected):
    np.random.seed(seed)
    X = np.random.randint(2, size=(25, 5), dtype=np.uint8)
    Y = np.random.randint(2, size=(25, 2), dtype=np.uint8)

    assert utils.ambiguous_patterns(X, Y, flatten=True) == expected


@pytest.mark.parametrize("seed,expected", [
    (2919627149, [[1, 9], [0, 2, 6, 10, 13], [3, 7], [5, 19], [4, 22]]),
    (1033918002, [[1, 19], [11, 13], [6, 12], [16, 22], [15, 18]]),
    (4129451494, [[19, 22], [11, 17], [5, 9, 10], [4, 12], [14, 16], [0, 7], [18, 20], [6, 24]]),
])
def test_duplicate_patterns_nonflat(seed, expected):
    np.random.seed(seed)
    X = np.random.randint(2, size=(25, 5), dtype=np.uint8)
    Y = np.random.randint(2, size=(25, 2), dtype=np.uint8)

    assert utils.ambiguous_patterns(X, Y, flatten=False) == expected

# @pytest.mark.parametrize("opname,Ni,No,Ne,Ns", [
#     ('add', 4, 1, 8, 50),
#     ('sub', 4, 2, 12, 50),
#     ('sub', 4, 2, 16, 50),
#     ('add', 8, 3, 4, 10),
#     ('mul', 8, 4, 64, 100),
#     ('and', 8, 4, 128, 10),
#     ('mul', 8, 8, 128, 150),
# ])
# def test_ambiguous_patterns(opname, Ni, No, Ne, Ns):
#     op = gen.operator_function(opname, Ni, No)
#     samples = gen.unique_valid_samples(op, Ni, No, Ns, Ne)

#     # generate output patterns from sample
#     filename = os.path.join(DATA_DIR, '{}{}.npy'.format(opname, Ni))
#     full_target = np.load(filename)
#     target_matrix = full_target[samples][:, :, :No]

#     assert np.all(np.any(target_matrix, axis=1))
#     assert not np.any(np.all(target_matrix, axis=1))
