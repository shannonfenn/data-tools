import re
import argparse
import rapidjson as json
from os.path import splitext


def filtered(line, key_regex):
    # record = json.loads(line, precise_float=True)
    record = json.loads(line)
    keys_to_remove = set()
    for key in record:
        if key_regex.fullmatch(key):
            keys_to_remove.add(key)
    record = {k: record[k] for k in record.keys() - keys_to_remove}
    return json.dumps(record)


def filter_file(infile, outfile, key_regex):
    line = infile.readline()
    line = filtered(line[1:], key_regex)   # first line starts with '['
    outfile.write('[' + line + '\n')
    for line in infile:
        # ignore the final line (it will be added back in later)
        if not line.startswith(']'):
            line = filtered(line[1:], key_regex)
            outfile.write(',' + line + '\n')
    outfile.write(']\n')


def main():
    parser = argparse.ArgumentParser(
        description='Filter long entries out of records.')
    parser.add_argument('infile', type=str)
    parser.add_argument('outfile', nargs='?', type=str)
    args = parser.parse_args()

    if args.outfile is None:
        base, ext = splitext(args.infile)
        args.outfile = base + '_filtered' + ext

    regex = re.compile('|'.join(['final_net', 'training_indices',
                                 'intermediate_network_\\d+']))

    with open(args.infile) as infile, open(args.outfile, 'w') as outfile:
        filter_file(infile, outfile, regex)


if __name__ == '__main__':
    main()
