#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import lzma
import os.path


def convert_line(line):
    line = line.strip()
    if line.startswith('[') or line.startswith(','):
        line = line[1:]
    if line.endswith(','):
        line = line[:-1]
    if line.startswith(']'):
        return None
    else:
        return line + '\n'


def is_ndjson(fname, open_method):
    with open_method(fname, 'rt') as f:
        return f.read(1) == '{'


def convert(infilename, open_method):
    base, ext = os.path.splitext(infilename)
    outfilename = base + '_ndjsonconverted' + ext

    print('Reading...')

    if is_ndjson(infilename, open_method):
        print('Already in ndjson format.')
        return

    with open_method(infilename, 'rt') as infile:
        lines = infile.readlines()

        print('Converting...')
        # not in ldjson format
        with open_method(outfilename, 'wt') as outfile:
            for line in lines:
                line = convert_line(line)
                if line:
                    outfile.write(line)
        print(f'done. Stored in {outfilename}')


def main():
    parser = argparse.ArgumentParser(description='convert json list to ndjson')
    parser.add_argument('file', type=str)
    parser.add_argument('--check', '-c', action='store_true',
                        help='Just check, don\'t attempt conversion.')
    # Process arguments
    args = parser.parse_args()

    if args.file.endswith('.xz'):
        open_method = lzma.open
    else:
        open_method = open

    if args.check:
        if is_ndjson(args.file, open_method):
            print('In ndjson format.')
        else:
            print('Not in ndjson format.')
    else:
        convert(args.file, open_method)


if __name__ == '__main__':
    main()
