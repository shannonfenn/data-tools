#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import lzma
import os.path


def convert(infilename):
    base, ext = os.path.splitext(infilename)
    outfilename = base + '_ndjsonconverted' + ext

    print('Reading...')

    with lzma.open(infilename) as infile:
        lines = infile.readlines()

    if lines[0].startswith(b'['):
        print('Converting...')
        # not in ldjson format
        with lzma.open(outfilename, 'w') as outfile:
            for line in lines:
                line = line[1:].strip()
                if line:
                    outfile.write(line + b'\n')
        print(f'done. Stored in {outfilename}')
    else:
        print('Already in ndjson format.')


def main():
    parser = argparse.ArgumentParser(description='convert json list to ndjson')
    parser.add_argument('file', type=str)
    # Process arguments
    args = parser.parse_args()

    convert(args.file)


if __name__ == '__main__':
    main()
