import xmltodict
from ncclient import manager
from pprint import pprint

CONNECTION = {
    'host': '192.168.30.22',
    'port': 830,
    'username': 'cisco',
    'password': 'cisco',
    'hostkey_verify': False

}

def print_intfs_xmltodict(connection):
    with manager.connect(**connection) as m:
        running_config_xml = m.get_config(source='running').data_xml

    running_config_dict = xmltodict.parse(running_config_xml, dict_constructor=dict)

    for intf_type,intfs in running_config_dict['data']['native']['interface'].items():
        for interface in intfs:
            if interface['ip'].get('address'):
                intf_name = interface['name']
                intf_ip = interface['ip']['address']['primary']['address']
                intf_mask = interface['ip']['address']['primary']['mask']
                print(f'You have interface with number {intf_name} and primary IP {intf_ip}/{intf_mask}')

if __name__ == '__main__':
    print_intfs_xmltodict(CONNECTION)
