import datatools.sampling as sampling
import numpy as np
import argparse
import os.path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate sample indices and '
        'ensure they are contain both 0 and 1 values for each target for the '
        'given operator and target number.')
    parser.add_argument('op', type=str,
                        choices=['zero', 'add', 'sub', 'mul', 'and', 'or'],
                        help='operator to validate for.')
    parser.add_argument('Ni', type=int, help='number of inputs (total)')
    parser.add_argument('No', type=int, help='number of outputs (must be <= '
                        'default for the given operator)')
    parser.add_argument('Ns', type=int,
                        help='number of different samples')
    parser.add_argument('Ne', type=int,
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

    # generate filename
    fname = '{}_{}_{}_dich_{}_{}.npy'.format(args.Ni, args.Ns, args.Ne,
                                             args.op, args.No)
    fname = os.path.join(args.dir, fname)
    # ensure file is writtable or force is set
    if not args.force and os.path.isfile(fname):
        raise ValueError('File exists and will not be overwritten', fname)
    # generate nontrivial samples
    samples = sampling.nontrivial_sampling(args.Ns, args.Ne, args.op,
                                           args.Ni, args.No)
    # Dump to file
    np.save(fname, samples)
