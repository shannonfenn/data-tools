import networkx as nx
import numpy as np
from itertools import chain


def build_digraph_from_network(net):
    gates, Ni, No = net.gates, net.Ni, net.No
    Ng = len(gates)
    G = nx.DiGraph()
    G.add_nodes_from(range(Ni))
    edgelist = []
    for g, gate in enumerate(gates):
        edgelist.append((gate[0], g + Ni))
        edgelist.append((gate[1], g + Ni))
    G.add_edges_from(edgelist)

    G.graph['Ni'] = int(Ni)
    G.graph['No'] = int(No)
    G.graph['Ng'] = int(Ng)

    return G


def last_connected_outputs(G):
    No = G.graph['No']
    num_nodes = G.number_of_nodes()
    last = [-1]*num_nodes
    for output in reversed(range(num_nodes - No, num_nodes)):
        for g in nx.ancestors(G, output):
            last[g] = output + No - num_nodes
    return last


def find_dangling(G):
    No = G.graph['No']
    dangling = set(G.nodes())
    for output in range(G.number_of_nodes() - No, G.number_of_nodes()):
        dangling -= {output}
        dangling -= set(nx.ancestors(G, output))
    return dangling


def connectivity(G):
    Ni, No, Ng = G.graph['Ni'], G.graph['No'], G.graph['Ng']
    connected = chain.from_iterable(nx.ancestors(G, Ni+Ng-o-1) for o in range(No))
    connected = np.unique(list(connected))
    return len(connected) / (Ng - No)


def greedy_compression_onepass(state, debug=False):
    # finds an smaller depth network with the same activation matrix
    Ni, Ng = state.Ni, state.Ng
    gates = np.asarray(state.gates)
    A = np.asarray(state.activation_matrix)
    assert all(gates[:, -1] == 7)
    modified = False
    for g in reversed(range(Ng)):
        c0, c1 = gates[g, :-1]
        c0_, c1_ = c0, c1  # So we can tell if a connection has been updated
        a_out = A[Ni+g]
        a0, a1 = A[c0], A[c1]

        # find earliest replacement for first connection
        for i in range(c0):
            if np.array_equal(a_out, ~(A[i] & a1)):
                modified = True
                c0_ = i
                if debug:
                    print('({0}, {1})->{2} replaced with ({3}, {1})->{2}'.format(
                        c0, c1, Ni+g, c0_))
        # replace it
        if c0 != c0_:
            c0 = c0_
            gates[g, 0] = c0
        # find earliest replacement for second connection (using new first connection if updated)
        for i in range(c1):
            if np.array_equal(a_out, ~(A[i] & a0)):
                modified = True
                c1_ = i
                if debug:
                    print('({0}, {1})->{2} replaced with ({0}, {3})->{2}'.format(
                        c0, c1, Ni+g, c1_))
        # replace it
        if c1 != c1_:
            c1 = c1_
            gates[g, 1] = c1
    return modified


def greedy_compression(state, debug=False):
    while greedy_compression_onepass(state, debug):
        pass
