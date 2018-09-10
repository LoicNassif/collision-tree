"""Graphing the graph"""

import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import reverseBFS

def travel_in_order(G, BST, label_dic):
    if BST._root is not None:
        travel_in_order(G, BST._left, label_dic)

        if BST._root.value[1] is None:
            G.add_node(BST._root.value[0], velocity=BST._root.value[2])
            label_dic[BST._root.value[0]] = float(0)
        else:
            G.add_node(BST._root.value[0]+"-"+BST._root.value[1], velocity=BST._root.value[2])
            label_dic[BST._root.value[0]+"-"+BST._root.value[1]] = float("{0:.3e}".format(BST._root.value[-1]))

        travel_in_order(G, BST._right, label_dic)
    return label_dic

def find_max(node_list, label_dic):
    max = node_list[0]
    max_index = 0
    for n in range(len(node_list)):
        if label_dic[node_list[n]] > label_dic[max]:
            max = node_list[n]
            max_index = n
    return max, max_index

def connect_graph(T, node_list, label_dic):
    if len(node_list) == 0:
        return None
    elif len(node_list) == 1:
        return node_list[0]
    else:
        max, max_index = find_max(node_list, label_dic)
        T.add_node(max)
        T.add_edge(max, connect_graph(T, node_list[:max_index], label_dic))
        T.add_edge(max, connect_graph(T, node_list[max_index+1:], label_dic))
        return max

def hierarchy_pos(G, root, width=10.5, vert_gap = 0.2, vert_loc = 0, xcenter = 0.5,
                  pos = None, parent = None):
    """Thanks to Joel for this function @
    https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-graphs-from-networkx-with-python-3"""

    if pos == None:
        pos = {root:(xcenter,vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)
    neighbors = G.neighbors(root)
    neighbors = list(neighbors)
    if len(neighbors)!=0:
        dx = width/len(neighbors)
        nextx = xcenter - width/2 - dx/2
        for neighbor in neighbors:
            nextx += dx
            pos = hierarchy_pos(G,neighbor, width = dx, vert_gap = vert_gap,
                                vert_loc = vert_loc-vert_gap, xcenter=nextx, pos=pos,
                                parent = root)
    return pos

#main()
def main(BST, ROOT_TITLE, Real_Mass, Fake_Mass, STD): # Written for BST input in mind
    # Create the graph
    G = nx.Graph()

    # depth = reverseBFS.compute_real_mass(BST)
    # Real_Mass = depth[0][0]._root.value[3][0]
    # STD = depth[0][0]._root.value[3][1]

    # Create the Tree
    T = nx.DiGraph()

    # Create a label dictionary
    label_dic = {}
    pos = {}

    # Add nodes in in-order
    label_dic = travel_in_order(G, BST, label_dic)

    # Have an attribute to color. In this example position of nodes
    from itertools import count
    # get unique groups
    # Thank you to Aric to set up the colorbar @
    # https://stackoverflow.com/questions/28910766/python-networkx-set-node-color-automatically-based-on-number-of-attribute-opt
    groups = set(nx.get_node_attributes(G,'velocity').values())
    mapping = dict(zip(sorted(groups),count()))
    nodes = G.nodes()
    colors = [mapping[G.node[n]['velocity']] for n in nodes]

    # Link up the nodes
    node_list = G.nodes()
    node_list = list(node_list)
    connect_graph(T, node_list, label_dic)
    maximum, _ = find_max(node_list, label_dic)
    pos = hierarchy_pos(T, maximum)

    # Draw the graph
    plt.figure()
    plt.title(ROOT_TITLE)
    ax = plt.gca()
    cmap=plt.cm.jet

    # for key in depth:
    #     print("key: "+str(key)+" value: ")
    #     for i in range(len(depth[key])):
    #         print(depth[key][i].value)
    # print()

    ax.text(1.5, 0, r"Real Mass = "+str("{0:.3e}".format(Real_Mass)) + "$\pm$" + str("{0:.3e}".format(STD)) +
            "\n"+"Fake Mass = "+str("{0:.3e}".format(Fake_Mass)), fontsize=6)

    ec = nx.draw_networkx_edges(T, pos, alpha=0.2)
    nc = nx.draw_networkx_nodes(T, pos, nodelist=nodes, node_color=colors,
                            with_labels=True, node_size=350, cmap=plt.cm.jet)
    nx.draw_networkx_labels(T, pos, font_size=8)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)

    plt.colorbar(nc, cax=cax)
    plt.show()



if __name__ == '__main__':
    main()
