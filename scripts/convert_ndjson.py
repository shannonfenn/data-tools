#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import lzma
import os.path


def convert(infilename, open_method):
    base, ext = os.path.splitext(infilename)
    outfilename = base + '_ndjsonconverted' + ext

    print('Reading...')

    with open_method(infilename, 'rt') as infile:
        if infile.read(1) == '{':
            print('Already in ndjson format.')
            return
        infile.seek(0)

        lines = infile.readlines()

        print('Converting...')
        # not in ldjson format
        with open_method(outfilename, 'wt') as outfile:
            for line in lines:
                line = line[1:].strip()
                if line:
                    outfile.write(line + '\n')
        print(f'done. Stored in {outfilename}')


def main():
    parser = argparse.ArgumentParser(description='convert json list to ndjson')
    parser.add_argument('file', type=str)
    # Process arguments
    args = parser.parse_args()

    if args.file.endswith('.xz'):
        open_method = lzma.open
    else:
        open_method = open

    convert(args.file, open_method)


if __name__ == '__main__':
    main()
