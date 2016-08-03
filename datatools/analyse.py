import palettable
import networkx as nx
import pandas as pd
from itertools import cycle
import sys
import os


INP_COLOUR = '#ff0000'
OUT_COLOUR = '#00ff00'
DANGLING_COLOUR = '#ffffff'
PALETTE = palettable.colorbrewer.qualitative.Set3_12.hex_colors


def get_network_from_result(result):
    gates = result['final_net']
    Ni, No = result['Ni'], result['No']
    return (gates, Ni, No)


def build_digraph_from_network(net):
    gates, Ni, No = net
    Ng = len(gates)
    G = nx.DiGraph()
    G.add_nodes_from(range(Ni))
    edges = []
    for g, gate in enumerate(gates):
        edges.append((gate[0], g + Ni))
        edges.append((gate[1], g + Ni))
    G.add_edges_from(edges)

    G.graph['Ni'] = int(Ni)
    G.graph['No'] = int(No)
    G.graph['Ng'] = int(Ng)

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


def draw(network, path=None):
    G = build_digraph_from_network(network)
    annotate_graph(G)
    if path:
        if not path.endswith('.graphml'):
            path += '.graphml'
        nx.write_graphml(G, path)
    else:
        nx.draw(G)


def create_graphs(directory, indices=None):
    result_filename = os.path.join(directory, 'results.json')
    graph_filename_base = os.path.join(directory, 'network_')
    results = pd.read_json(result_filename)
    if not indices:
        indices = range(len(results))
    for i in indices:
        graph_filename = graph_filename_base + '{}.graphml'.format(i)
        net = get_network_from_result(results.iloc[i])
        draw(net, graph_filename)


def main(argv):
    pass

if __name__ == '__main__':
    main(sys.argv)
