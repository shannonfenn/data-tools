#! /usr/bin/env python

import os.path
import argparse
import rapidjson as json


def collapse_linear(record):
    replacement_patterns = {'trg_errs': 'trg_err_tgt_{}',
                            'test_errs': 'test_err_tgt_{}',
                            'trg_mccs': 'trg_mcc_tgt_{}',
                            'test_mccs': 'test_mcc_tgt_{}'}
    if 'trg_errs' not in record:
        n = record['No']
        for new_key, group_format_str in replacement_patterns.items():
            old_keys = [group_format_str.format(i) for i in range(n)]
            vals = [record.pop(k) for k in old_keys]
            record[new_key] = vals
    return record


def collapse_square(record):
    new_key = 'feature_sets'
    if new_key not in record:
        n = record['No']
        key_fmt_string = 'fs_s{}_t{}'
        vals = []
        for s in range(n):
            row_keys = [key_fmt_string.format(s, t) for t in range(n)]
            row = [record.pop(key, None) for key in row_keys]
            vals.append(row)
        record[new_key] = vals
    return record


def filter_file(istream, ostream):
    for line in istream:
        # ignore the final line (it will be added back in later)
        if not line.startswith(']'):
            sep, line = line[0], line[1:]
            record = json.loads(line)
            record = collapse_linear(collapse_square(record))
            line = json.dumps(record)
            ostream.write(sep + line + '\n')
        else:
            ostream.write(line)


def main():
    parser = argparse.ArgumentParser(
        description='Collapse per target keys into single key.')
    parser.add_argument('infile', type=str)
    parser.add_argument('outfile', nargs='?', type=str)
    args = parser.parse_args()

    if args.outfile is None:
        base, ext = os.path.splitext(args.infile)
        args.outfile = base + '_collapsed' + ext

    assert args.infile != args.outfile

    with open(args.infile) as infile, open(args.outfile, 'w') as outfile:
        filter_file(infile, outfile)


if __name__ == '__main__':
    main()
