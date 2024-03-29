#! /usr/bin/env python

import re
import argparse
import rapidjson as json
from os.path import splitext


def remove_keys(record, key_regex):
    # record = json.loads(line, precise_float=True)
    keys_to_remove = set()
    for key in record:
        if key_regex.fullmatch(key):
            keys_to_remove.add(key)
    record = {k: record[k] for k in record.keys() - keys_to_remove}
    return record


def filter_file(istream, ostream, key_regex):
    for line in istream:
        record = json.loads(line)
        record = remove_keys(record, key_regex)
        ostream.write(json.dumps(record))
        ostream.write('\n')


def main():
    parser = argparse.ArgumentParser(
        description='Filter long entries out of records.')
    parser.add_argument('infile', type=str)
    parser.add_argument('outfile', nargs='?', type=str)
    args = parser.parse_args()

    if args.outfile is None:
        base, ext = splitext(args.infile)
        args.outfile = base + '_filtered' + ext

    regex = re.compile('|'.join([
        'final_net', 'training_indices',
        'intermediate_network_\\d+',
        'max_depth_tgt_\\d+']))

    assert args.infile != args.outfile

    with open(args.infile) as infile, open(args.outfile, 'w') as outfile:
        filter_file(infile, outfile, regex)


if __name__ == '__main__':
    main()
