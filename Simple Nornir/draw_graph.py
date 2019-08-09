# Based on http://matthiaseisen.com/articles/graphviz/
import graphviz as gv
from pprint import pprint
styles = {
    'graph': {
        'label': 'LAB Map',
        'fontsize': '16',
        'fontcolor': 'white',
        'bgcolor': '#333333',
        'rankdir': 'BT',
    },
    'nodes': {
        'fontname': 'Helvetica',
        'shape': 'box3d',
        'fontcolor': 'white',
        'color': '#006699',
        'fillcolor': '#006699',
        'margin': '0.3',
    },
    'edges': {
        'style': 'dashed',
        'color': 'green',
        'arrowhead': 'open',
        'fontname': 'Courier',
        'fontsize': '10',
        'fontcolor': 'black',
        'splines': 'curved',
    }
}

def apply_styles(graph, styles):
    graph.graph_attr.update(('graph' in styles and styles['graph']) or {})
    graph.node_attr.update(('nodes' in styles and styles['nodes']) or {})
    graph.edge_attr.update(('edges' in styles and styles['edges']) or {})
    return graph

def form_node_set(topology_dict):
    ''' Parse a topology dictionary and form a node set.
    ARGS:
        topology_dict(dict) - dictionary in the following format:
        {('SW5', 'Et0/0'): [('R4', 'Et0/0')],
         ('SW5', 'Et0/1'): [('R1', 'Et0/0')],
         ('SW6', 'Et0/0'): [('R2', 'Et0/0')],
         ('SW6', 'Et0/1'): [('R1', 'Et0/1')],
         ('SW7', 'Et0/0'): [('R4', 'Et0/1')],
         ('SW7', 'Et0/1'): [('R3', 'Et0/0')],
         ('SW8', 'Et0/0'): [('R2', 'Et0/1')],
         ('SW8', 'Et0/1'): [('R3', 'Et0/1')]}
    RETURNS:
        node_list(set) - a set of nodes
    '''
    node_list = []
    for local, remote in topology_dict.items():
        node_list.append(local[0])
        for connection in remote:
            node_list.append(connection[0])
    return set(node_list)

def form_edge_list(topology_dict):
    ''' Parse a topology dictionary and form a edge list (links).
    ARGS:
        topology_dict(dict) - dictionary in the following format:
        {('SW5', 'Et0/0'): [('R4', 'Et0/0')],
         ('SW5', 'Et0/1'): [('R1', 'Et0/0')],
         ('SW6', 'Et0/0'): [('R2', 'Et0/0')],
         ('SW6', 'Et0/1'): [('R1', 'Et0/1')],
         ('SW7', 'Et0/0'): [('R4', 'Et0/1')],
         ('SW7', 'Et0/1'): [('R3', 'Et0/0')],
         ('SW8', 'Et0/0'): [('R2', 'Et0/1')],
         ('SW8', 'Et0/1'): [('R3', 'Et0/1')]}
    RETURNS:
        edge_list(list) - list of dicionaries ready to paste into graphviz edge functiona.
            [{'head_name': 'SW5',
              'headlabel': 'Et0/1',
              'tail_name': 'R1',
              'taillabel': 'Et0/0'},
             {'head_name': 'SW5',
              'headlabel': 'Et0/3',
              'tail_name': 'SW7',
              'taillabel': 'Et0/2'}]
    '''
    edge_list = []
    edge_dict_keys = ['head_name', 'tail_name', 'headlabel', 'taillabel']
    for local, remote in topology_dict.items():
        for connection in remote:
            edge_dict_values = [local[0], connection[0], local[1], connection[1]]
            edge_dict = dict(zip(edge_dict_keys, edge_dict_values))
            edge_list.append(edge_dict)
    return edge_list

def draw_topology(topology_dict, output_filename='topology', engine = 'circo'):
    g1 = gv.Graph(format='svg', engine=engine)
    g1 = apply_styles(g1, styles)

    print('### Forming node list...')
    for node in form_node_set(topology_dict):
        g1.node(node)

    print('### Forming edges...')
    for edge in form_edge_list(topology_dict):
        g1.edge(**edge)

    print(f'### Rendering a topology graph {output_filename}.svg...')
    filename = g1.render(filename=output_filename)
