import numpy as np


def numpy_to_weka(filename, relation_name, attribute_details, attributes, comments=[]):
    """ writes NumPy arrays with data to WEKA format .arff files

        input: relation_name (string with a description), attribute_details (list 
        of the names of different attributes), attributes (array of attributes, 
        one row for each attribute, WEKA treats last row as classlabels by 
        default), comment (short description of the content)."""

    num_examples, num_attributes = attributes.shape
    if num_attributes != len(attribute_details):
        raise Exception('Number of attribute names != length of attributes')

    header = ''
    for comment in comments:
        header += '% {}\n'.format(comment)
    header += '@RELATION {}\n'.format(relation_name)

    for name, dtype in attribute_details.items():
        # assume values are numeric
        header += '@ATTRIBUTE {} {}\n'.format(name, dtype)

    header += '\n@DATA\n'

    if np.issubdtype(attributes.dtype, np.integer):
        fmt = '%d'
    else:
        fmt = '%.18e'

    np.savetxt(filename, attributes, fmt=fmt, delimiter=',', header=header)
