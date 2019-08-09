''' Grab LLDP table from devices using Nornir(NAPALM) and create a graph of the topology'''

import re

from nornir import InitNornir
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result
from pprint import pprint

from draw_graph import draw_topology

def name_from_fqdn(fqdn):
    return fqdn.split('.')[0]

def cisconify_intf(interface_name):
    ''' Convert interface name.
    Simply convert "Ethernet0/1" to "Et0/1"
    or "GigabitEthernet2/1" to "Gi2/1". You get the idea.'''
    intf_splitted = re.split('(\d+/\d+)', interface_name)
    intf_short = intf_splitted[0][0:2]+intf_splitted[1]
    return intf_short

def get_lldp_dict(hosts, verbose = False):
    ''' Run a Nornir task NAPALM_GET to collect LLDP neighbors from devices.
    ARGS:
        hosts - Nornir filtered object
    RETURNS:
        lldp_table_dict(dict) - raw LLDP data gathered from hosts in the following format:

    {'SW5': {'Ethernet0/0': [{'hostname': 'R4.lab.hi', 'port': 'Et0/0'}],
         'Ethernet0/1': [{'hostname': 'R1.lab.hi', 'port': 'Et0/0'}],
         'Ethernet0/2': [{'hostname': 'SW6.lab.hi', 'port': 'Et0/2'}],
         'Ethernet0/3': [{'hostname': 'SW7.lab.hi', 'port': 'Et0/2'}]}}
    '''
    print(f'### Running LLDP get for selected devices...{[host for host in hosts.inventory.hosts.keys()]}')
    lldp_table = hosts.run(task=networking.napalm_get, getters=["get_lldp_neighbors"])
    lldp_table_dict = {}
    for item, value in lldp_table.items():
        lldp_table_dict[item] = value.result['get_lldp_neighbors']
    if verbose:
        print_result(lldp_table)
    return lldp_table_dict

def beauitify_lldp_dict(raw_lldp_dict):
    ''' Initialy beautify the raw dict gotten from Nornir.
    ARGS:
        raw_lldp_dict(dict) - LLDP dict from Nornir. See format in get_lldp_dict's docstring.
    RETURNS:
        beauity_dct(dict) - the dictionary in the following format:
        {('SW5', 'Et0/0'): [('R4', 'Et0/0')],
         ('SW5', 'Et0/1'): [('R1', 'Et0/0')]}
    '''
    print('### Beautifying the output...')
    beauity_dct = {}
    for src_hst, connections in raw_lldp_dict.items():
        for src_intf, connection_list in connections.items():
            src_intf_short = cisconify_intf(src_intf)
            beauity_dct[(src_hst, src_intf_short)] = []
            for connection in connection_list:
                remote_end = (name_from_fqdn(connection['hostname']), connection['port'])
                beauity_dct[(src_hst, src_intf_short)].append(remote_end)
    return beauity_dct

def remove_duplicates(beauity_dct):
    ''' Removing duplicated from beautified dictionary. A little bit agly, should be rewritten...
    ARGS:
        beauity_dct(dict) - pre parsed LLDP dictionary. See the format in beauitify_lldp_dict.
    RETURNS:
        connection_dict(dict) - dict with is ready for graphing in the same format, but w/o duplicates.
    '''
    print('### Removing duplicated...')
    connection_dict = {}
    conenction_keys = []
    for local_end, remote_end in beauity_dct.items():
        conenction_keys.append(local_end)
        for connection in remote_end:
            if connection not in conenction_keys:
                connection_dict[local_end] = []
                connection_dict[local_end].append(connection)
    return connection_dict

def prepare_dict(lldp_table_dict):
    ''' Just a combination of beauitify_lldp_dict and remove_duplicates functions.
    Might be a oneliner like this.
    return remove_duplicates(beauitify_lldp_dict(lldp_table_dict))
    '''
    beauity_dct = beauitify_lldp_dict(lldp_table_dict)
    connection_dict = remove_duplicates(beauity_dct)
    return connection_dict

def main():
    '''
    Initiate Nornir with a config.
    Filter all hosts
    Run LLDP task
    Reformat a dictionary
    Pass to draw_topology function
    Enjoy!
    '''
    nr = InitNornir(config_file="config.yaml")
    all_hosts = nr.filter()

    lldp_table_dict = get_lldp_dict(all_hosts, verbose = True)
    graph_dct = prepare_dict(lldp_table_dict)
    draw_topology(graph_dct, engine='sfdp')

if __name__ == '__main__':
    main()
