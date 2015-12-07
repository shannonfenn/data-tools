import re
import rapidjson as json
import argparse


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
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('outfile', type=argparse.FileType('w'))
    args = parser.parse_args()

    regex = re.compile('|'.join(['final_network', 'training_indices',
                                 'intermediate_network_\\d+']))

    filter_file(args.infile, args.outfile, regex)


if __name__ == '__main__':
    main()
