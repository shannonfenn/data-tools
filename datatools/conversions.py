import numpy as np


def numpy_to_weka(ostream, relation_name, att_names, attributes, comment=''):
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

    np.savetxt(ostream, attributes, fmt='%d', delimiter=',', header=header)


def abk_file(ostream, features, target):
    n_examples, n_features = features.shape

    feature_numbers = np.reshape(np.arange(n_features), (n_features, 1))

    abk_data = np.hstack((feature_numbers, features.T))

    sample_names = '\t'.join('s' + str(i) for i in range(n_examples))

    header = 'FEATURESINROWS\nTARGETPRESENT\nLAST\n{}\n{}\ndummy\t{}'.format(
        n_features, n_examples, sample_names)

    target_row = '\t' + '\t'.join(str(x) for x in target) + '\n'

    np.savetxt(ostream, abk_data, fmt='%d', delimiter='\t',
               header=header, footer=target_row, comments='')
