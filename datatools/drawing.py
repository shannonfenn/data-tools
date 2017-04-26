import palettable
import numpy as np
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout, write_dot
import datatools.network as nt
import datatools.utils as utils
from itertools import cycle


def annotate_graph(G, layerwise_colouring=False, uncolour_dangling=False):
    palette = palettable.colorbrewer.qualitative.Set1_3.hex_colors
    INP_COLOUR = palette[0]
    INT_COLOUR = palette[1]
    OUT_COLOUR = palette[2]
    DANGLING_COLOUR = '#ffffff'

    Ni, No, Ng = G.graph['Ni'], G.graph['No'], G.graph['Ng']

    for i in range(Ng+Ni):
        G.node[i]['label'] = '{}'.format(i)

    for i in range(Ni):
        G.node[i]['color'] = INP_COLOUR

    for i in range(Ni+Ng-No, Ni+Ng):
        G.node[i]['color'] = OUT_COLOUR

    if layerwise_colouring:
        palette2 = palettable.colorbrewer.qualitative.Set3_12.hex_colors
        color_cycle = cycle(palette2)
        color_map = [next(color_cycle) for o in range(No)]

        label_last_connected_output(G)
        for g in range(Ni, Ng+Ni):
            if 'connected_output' in G.node[g]:
                G.node[g]['color'] = color_map[G.node[g]['connected_output']]
    else:
        for i in range(Ni, Ng+Ni-No):
            G.node[i]['color'] = INT_COLOUR

    if uncolour_dangling:
        dangling = nt.find_dangling(G)
        for d in dangling:
            G.node[d]['color'] = DANGLING_COLOUR


def label_last_connected_output(G):
    last = nt.last_connected_outputs(G)
    for g, l in enumerate(last):
        G.node[g]['connected_output'] = l


def draw_bn(G, ax, show_dangling=True, node_size=400, reposition=False):
    # fig, ax = plt.subplots()
    annotate_graph(G)
    pos = nx.drawing.nx_agraph.graphviz_layout(G, 'dot')

    if show_dangling:
        # de-emphasise dangling nodes
        colours = [G.node[g]['color'] for g in G.nodes_iter()]
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colours,
                               node_size=node_size)
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=nt.find_dangling(G),
                               node_color='w', node_size=node_size, alpha=0.75)
    else:
        G.remove_nodes_from(nt.find_dangling(G))
        if reposition:
            pos = nx.drawing.nx_agraph.graphviz_layout(G, 'dot')
        colours = [G.node[g]['color'] for g in G.nodes_iter()]
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colours,
                               node_size=node_size)

    nx.draw_networkx_edges(G, pos, ax=ax, width=0.1, alpha=0.9)

    labels = {g: G.node[g]['label'] for g in G.nodes_iter()}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=16)

    ax.axis('off')


def fs_dependency_graph(F, R, a_thresh=0, r_thresh=0.0):
    G = nx.DiGraph()

    for i, f in enumerate(F):
        G.add_node(i, fs=f)

    ranks, inverse = np.unique(R, return_inverse=True)
    for i in range(1, len(ranks)):
        for i0 in range(0, i):
            locs0 = np.where(inverse == i0)[0]
            locs1 = np.where(inverse == i)[0]

            for l0 in locs0:
                for l1 in locs1:
                    a_overlap = len(set(F[l0]).intersection(F[l1]))
                    r_overlap = utils.overlap(F[l0], F[l1])
                    if (a_overlap > a_thresh and r_overlap > r_thresh):
                        G.add_edge(l0, l1, a=a_overlap, r=r_overlap)

    return G


def draw_dependency_graph(F, R=None, a_thresh=0, r_thresh=0.0,
                          path=None, **nxargs):
    if R is None:
        R = [len(f) for f in F]

    G = fs_dependency_graph(F, R, a_thresh, r_thresh)

    pos = graphviz_layout(G, 'dot')
    weights = nx.get_edge_attributes(G, 'a')
    nodelabels = {n: '{} [{}]'.format(n, len(d['fs']))
                  for n, d in G.nodes_iter(data=True)}
    if path is None:
        nx.draw(G, pos, labels=nodelabels, edge_labels=weights, **nxargs)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=weights)
    else:
        nx.set_edge_attributes(G, 'label', weights)
        G = nx.relabel_nodes(G, nodelabels)
        write_dot(G, path)
