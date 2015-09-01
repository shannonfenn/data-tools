from collections import defaultdict
import numpy
import sys
import json
import palettable
import networkx as nx
from itertools import cycle
sys.path.append('/home/shannon/HMRI/code/boolnet/')
from boolnet.network.boolnetwork import BoolNetwork


INP_COLOUR = '#ff0000'
OUT_COLOUR = '#00ff00'
DANGLING_COLOUR = '#ffffff'
PALETTE = palettable.colorbrewer.qualitative.Set3_12.hex_colors


def get_network_from_result(result):
    connection_matrix = result['final_network']
    Ni, No = result['Ni'], result['No']
    return BoolNetwork(connection_matrix, Ni, No)


def build_digraph_from_network(net):
    Ni, No, Ng = net.Ni, net.No, net.Ng
    gates = net.gates
    G = nx.DiGraph()
    G.add_nodes_from(range(Ni))
    edges = []
    for g, gate in enumerate(gates):
        edges.append((gate[0], g + Ni))
        edges.append((gate[1], g + Ni))
    G.add_edges_from(edges)

    G.graph['Ni'] = Ni
    G.graph['No'] = No
    G.graph['Ng'] = Ng

    return G


def annotate_graph(G):
    Ni, No, Ng = G.graph['Ni'], G.graph['No'], G.graph['Ng']
    color_cycle = cycle(PALETTE)
    color_map = [next(color_cycle) for o in range(No)]

    for i in range(Ni):
        G.node[i]['label'] = '{}'.format(i)
        G.node[i]['color'] = INP_COLOUR

    label_latest_connected_output(G)
    for g in range(Ni, Ng+Ni):
        G.node[g]['label'] = '{}'.format(g)
        if 'connected_output' in G.node[g]:
            G.node[g]['color'] = color_map[G.node[g]['connected_output']]

    for o in range(No):
        idx = G.number_of_nodes() - No + o
        G.node[idx]['color'] = OUT_COLOUR

    dangling = find_dangling(G)
    for d in dangling:
        G.node[d]['color'] = DANGLING_COLOUR


def label_latest_connected_output(G):
    No = G.graph['No']
    num_nodes = G.number_of_nodes()
    for output in reversed(range(num_nodes - No, num_nodes)):
        for g in nx.ancestors(G, output):
            G.node[g]['connected_output'] = output + No - num_nodes


def find_dangling(G):
    No = G.graph['No']
    dangling = set(G.nodes())
    for output in range(G.number_of_nodes() - No, G.number_of_nodes()):
        dangling -= {output}
        dangling -= set(nx.ancestors(G, output))
    return dangling


def draw(result, path=None):
    G = build_digraph_from_network(get_network_from_result(result))
    annotate_graph(G)
    if path:
        if not path.endswith('.graphml'):
            path += '.graphml'
        nx.write_graphml(G, path)
    else:
        nx.draw(G)


def collate(run_data):
    results = run_data['results']

    collated = defaultdict(list)
    for result in results:
        for key, val in result.items():
            collated[key].append(val)
    return collated


def compare(filenames):
    experiment_names = []
    collated_results = []
    for filename in filenames:
        with open(filename) as f:
            raw = json.load(f)
        collated_results.append(collate(raw))
        experiment_names.append(raw['settings']['name'])

    import prettyplotlib as ppl
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    rcParams.update({'figure.autolayout': True})

    attributes = ['Full Error (simple)',
                  'time']
    for plt_num, attribute in enumerate(attributes):
        fig, axs = plt.subplots()
        fig.autofmt_xdate()
        # fig.set_figwidth( 2 * fig.get_figwidth() )
        # fig.set_figheight( 2 * fig.get_figheight() )
        data = [result[attribute] for result in collated_results]
        positions = numpy.arange(len(data)) + 0.5
        ppl.boxplot(axs, data, positions=positions, xticklabels=experiment_names)
        axs.set_ylim(bottom=0)
        axs.set_title(attribute)
        plt.savefig(attribute + '.png', bbox_inches='tight', orientation='portrait')


def main(argv):
    if len(argv) > 2:
        compare(argv[1:])
    elif len(argv) == 2:
        with open(argv[1]) as f:
            data = json.load(f)
            generate_graphs(data)
    else:
        print('ARGS!')

if __name__ == '__main__':
    main(sys.argv)
