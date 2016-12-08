import palettable
import networkx as nx
import datatools.network as nt
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
