import argparse
import operator
import os.path
import numpy as np


OPERATOR_MAP = {
    'add': operator.add,
    'sub': operator.sub,
    'mul': operator.mul,
    'div': operator.floordiv,
}


def to_binary(val, Nb):
    return [int(i) for i in '{:0{w}b}'.format(val, w=Nb)][::-1][:Nb]


def operator_function(operator_name, Ni, No):
    if Ni % 2:
        raise ValueError('Only binary operators supported, Ni must be even.')

    Nb = Ni // 2

    if No > Nb:
        raise ValueError('No > Ni/2. All supported operators have a maximum '
                         'output width of Ni/2')

    op = OPERATOR_MAP[operator_name]

    return lambda x: to_binary(op(int(x // Nb), int(x % Nb)), No)


def check_samples(samples):
    # check each row has distinct elements
    Ns, Ne = samples.shape
    for s in range(Ns):
        if len(set(samples[s])) < Ne:
            raise RuntimeError('Error: sample with duplicate indices')

    num_duplicates = 0
    for s in range(Ns):
        for s2 in range(s+1, Ns):
            if np.array_equal(samples[s], samples[s2]):
                num_duplicates += 1

    if num_duplicates > 0:
        print('Warning: {} samples are duplicated for Ns={}, Ne={}. This is '
              'unavoidable for Ns >= |samples| choose Ne but can also happen '
              'by chance otherwise. You may need to run this tool again.'.
              format(num_duplicates, Ns, Ne))


def construct_dichotomous_sample_base(operator, Ni, No):
    ''' Generates between log2(No) and No + 1 examples such that there is at
        least one example with each target value for each target (that is:
        there is a function expressed by the examples for each target).'''
    # generate one example randomly
    r = np.uint64(np.random.randint(2**Ni))
    so_far = set([r])
    targets_so_far = [set()] * No

    for o in range(No):
        # record the target value (for this target) of all existing examples
        for example in so_far:
            T = operator(r)
            targets_so_far[o].add(T[o])
        # only generate new samples if the existing  are not dichotomous for
        # this target note that there will always be at least one value present
        # since we generate an initial random example
        if len(targets_so_far[o]) < 2:
            r = np.uint64(np.random.randint(2**Ni))
            while operator(r)[o] in targets_so_far[o]:
                r = np.uint64(np.random.randint(2**Ni))
            so_far.add(r)
    return so_far


def single_unique_valid_sample(operator, Ni, No, Ne, output_vector):
    so_far = construct_dichotomous_sample_base(operator, Ni, No)

    # print(so_far)

    for i, example in enumerate(so_far):
        output_vector[i] = example

    for i in range(len(so_far), Ne):
        r = np.uint64(np.random.randint(2**Ni))
        # k = 0
        # print('\n', r, so_far)
        # ensure we sample without replacement
        while r in so_far:
            r = np.uint64(np.random.randint(2**Ni))
            # k += 1
            # if k > 4:
            #     raise ValueError
            # print(r, so_far)
        output_vector[i] = r
        so_far.add(r)


def unique_valid_samples(operator, Ni, No, Ns, Ne):
    if Ne > 2**Ni:
        raise ValueError('Cannot draw {} unique patterns of {} bits.'
                         .format(Ne, Ni))

    samples = np.zeros(shape=(Ns, Ne), dtype=np.uint64)

    for i in range(Ns):
        single_unique_valid_sample(operator, Ni, No, Ne, samples[i])

    return samples


def generate_and_dump_samples(operator_name, Ni, No, num_samples,
                              sample_size, directory, force):
    # generate filename and ensure it is writtable or force is set
    fname = '{}_{}_{}_{}_{}.npy'.format(
        Ni, num_samples, sample_size, operator_name, No)
    fname = os.path.join(directory, fname)
    if not force and os.path.isfile(fname):
        raise ValueError('File exists and will not be overwritten', fname)

    # get operator function from name
    operator = operator_function(operator_name, Ni, No)

    # choose (Ns x Ne) random integers without replacement
    samples = unique_valid_samples(Ni, num_samples, sample_size, operator)

    # check the samples for errors
    check_samples(samples)

    # Dump to file
    np.save(fname, samples)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate sample indices and '
        'ensure they are contain both 0 and 1 values for each target for the '
        'given operator and target number.')
    parser.add_argument('operator', type=str, choices=OPERATOR_MAP.keys(),
                        help='operator to validate for.')
    parser.add_argument('Ni', type=int, help='number of inputs (total)')
    parser.add_argument('No', type=int, help='number of outputs (must be <= '
                        'default for the given operator)')
    parser.add_argument('num_samples', type=int,
                        help='number of different samples')
    parser.add_argument('sample_size', type=int,
                        help='number of examples in each sample')
    parser.add_argument('--force', '-f', action="store_true",
                        help='force overwriting of files')
    parser.add_argument('--dir', type=str,
                        default='~/HMRI/experiments/datasets/samples',
                        help='directory to store file')

    args = parser.parse_args()

    if args.sample_size < args.No + 1:
        raise ValueError('Sample sizes below No + 1 are not supported. In the '
                         'worst case this many examples are needed to ensure '
                         'dichotomous target values for all targets and this '
                         'is the number of initial samples the greedy '
                         'construction heuristic will generate.')

    args.dir = os.path.expanduser(args.dir)

    if not os.path.isdir(args.dir):
        raise OSError('Directory does not exist: {}'.format(args.dir))

    generate_and_dump_samples(
        args.operator, args.Ni, args.No, args.num_samples,
        args.sample_size, args.dir, args.force)


# for Ne in range(8, 256):
#     generate_and_dump_samples(
#         8, 3, Ne, '/home/shannon/HMRI/fiddle/kFS metrics')
# l = [2**i for i in range(4, 16)]
# k = [l[0]]
# for i in range(len(l)-1):
#     k.append(l[i+1])
#     k.append(l[i] + l[i+1])
# for Ne in k:
#     generate_and_dump_samples(
#         16, 3, Ne, '/home/shannon/HMRI/fiddle/kFS metrics')
