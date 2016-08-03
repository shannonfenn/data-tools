import numpy as np


def numpy_to_weka(filename, relation_name, att_names, attributes, comment=''):
    """ writes NumPy arrays with data to WEKA format .arff files

        input:  relation_name (string with a description),
                att_names (list of attribute names),
                attributes (array of attributes),
                comment (short description of the content)."""

    _, num_attributes = attributes.shape
    if num_attributes != len(att_names):
        raise Exception('Number of attribute names != length of attributes')

    header = '% {}\n'.format(comment)
    header += '@RELATION {}\n'.format(relation_name)

    for name in att_names:
        # assume values are numeric
        header += '@ATTRIBUTE {} NUMERIC\n'.format(name)

    header += '\n@DATA\n'

    np.savetxt(filename, attributes, fmt='%d', delimiter=',', header=header)
