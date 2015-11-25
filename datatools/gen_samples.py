import argparse
import os.path
import numpy as np


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


def generate_and_dump_samples(Ni, Ns, Ne, directory, force):
    if Ne > 2**Ni:
        raise ValueError('Cannot draw {} unique patterns of {} bits.'
                         .format(Ne, Ni))

    # choose (Ns x Ne) random integers without replacement
    samples = np.zeros(shape=(Ns, Ne), dtype=np.uint64)
    for i in range(Ns):
        so_far = set()
        for k in range(Ne):
            r = np.uint64(np.random.randint(2**Ni))
            while r in so_far:
                r = np.uint64(np.random.randint(2**Ni))
            samples[i][k] = r
            so_far.add(r)

    # check the samples for errors
    check_samples(samples)

    # Dump to file
    fname = '{}_{}_{}.npy'.format(Ni, num_samples, sample_size)
    fname = os.path.join(directory, fname)
    if not force and os.path.isfile(fname):
        raise ValueError('File exists and will not be overwritten', fname)
    np.save(fname, samples)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate sample indices.')
    parser.add_argument('Ni', type=int, help='number of inputs (total)')
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

    args.dir = os.path.expanduser(args.dir)

    if not os.path.isdir(args.dir):
        raise OSError('Directory does not exist: {}'.format(args.dir))

    generate_and_dump_samples(args.Ni, args.num_samples,
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
