#! /usr/bin/env python

import datatools.sampling as sampling
import numpy as np
import argparse
import os.path


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

    # generate filename
    fname = '{}_{}_{}.npy'.format(args.Ni, args.Ns, args.Ne)
    fname = os.path.join(args.dir, fname)
    # ensure file is writtable or force is set
    if not args.force and os.path.isfile(fname):
        raise ValueError('File exists and will not be overwritten', fname)

    # generate samples
    samples = sampling.simple_sampling(args.Ns, args.Ne, 2**args.Ni)

    np.save(fname, samples)
