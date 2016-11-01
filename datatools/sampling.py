import numpy as np


def to_binary(val, Nb):
    return [int(i) for i in '{:0{w}b}'.format(val, w=Nb)][::-1][:Nb]


def operator_function(operator_name, Ni, No):
    Nb = Ni // 2
    d = 2**Nb

    if operator_name == 'zero':
        return lambda x: 0
    elif operator_name == 'add':
        return lambda x: to_binary(int(x // d) + int(x % d), No)
    elif operator_name == 'sub':
        return lambda x: to_binary((int(x // d) - int(x % d)) % d, No)
    elif operator_name == 'mul':
        return lambda x: to_binary(int(x // d) * int(x % d), No)
    elif operator_name == 'and':
        return lambda x: to_binary(int(x // d) & int(x % d), No)
    elif operator_name == 'or':
        return lambda x: to_binary(int(x // d) | int(x % d), No)
    else:
        raise ValueError('no such operator: {}')


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


def construct_nontrivial_sample_base(operator, Ni, No):
    ''' Generates between log2(No) and No + 1 examples such that there is at
        least one example with each target value for each target (that is:
        there is a function expressed by the examples for each target).'''
    # generate one example randomly
    r = np.uint64(np.random.randint(2**Ni))
    so_far = set([r])
    targets_so_far = [set() for i in range(No)]

    for o in range(No):
        # record the target value (for this target) of all existing examples
        for example in so_far:
            T = operator(example)
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


def single_nontrivial_sample(operator, Ni, No, Ne, output_vector):
    so_far = construct_nontrivial_sample_base(operator, Ni, No)

    for i, example in enumerate(so_far):
        output_vector[i] = example

    for i in range(len(so_far), Ne):
        r = np.uint64(np.random.randint(2**Ni))
        while r in so_far:
            r = np.uint64(np.random.randint(2**Ni))
        output_vector[i] = r
        so_far.add(r)


def nontrivial_sampling(Ns, Ne, operator_name, Ni, No):
    # get operator function from name
    operator = operator_function(operator_name, Ni, No)

    if Ne > 2**Ni:
        raise ValueError('Cannot draw {} unique patterns of {} bits.'
                         .format(Ne, Ni))

    samples = np.zeros(shape=(Ns, Ne), dtype=np.uint64)

    for i in range(Ns):
        single_nontrivial_sample(operator, Ni, No, Ne, samples[i])

    check_samples(samples)  # for errors
    return samples


def simple_sampling(Ns, Ne, N):
    # choose (Ns x Ne) random integers without replacement
    samples = np.zeros(shape=(Ns, Ne), dtype=np.uint64)
    for i in range(Ns):
        so_far = set()
        for k in range(Ne):
            r = np.uint64(np.random.randint(N))
            while r in so_far:
                r = np.uint64(np.random.randint(N))
            samples[i][k] = r
            so_far.add(r)

    check_samples(samples)  # for errors
    return samples
