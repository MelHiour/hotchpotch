import xmltodict
from jinja2 import Environment, FileSystemLoader
from ncclient import manager
from pprint import pprint

CONNECTION = {
    'host': '192.168.30.22',
    'port': 830,
    'username': 'cisco',
    'password': 'cisco',
    'hostkey_verify': False

}

CONFIG_DATA = {
'loopbacks': [
    {'id': '0',
    'description': 'Loopback number one',
    'address': '10.1.1.1',
    'netmask': '255.255.255.0'
    },
    {'id': '1',
    'description': 'Loopback number two',
    'address': '10.1.1.2',
    'netmask': '255.255.255.0'
    }
]
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

def cfg_from_template(template_file, params, template_dir='templates'):
    """ Generate a configuration from template using parameters.
    ARGS:
        template_file(str) - name of Jinja2 template filename
        params - parameters for templating. Usually dict.
        template_dir - path to template dir ('tempaltes' by default)
    RETURNS:
        Just a rendered template
    """
    env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(template_file)
    return template.render(params)

def config_device(connection, config_data, template):
    configuration = cfg_from_template(template, config_data)
    with manager.connect(**connection) as m:
        result = m.edit_config(target='running', config=configuration)

if __name__ == '__main__':
    config_device(CONNECTION, CONFIG_DATA, 'loopback-template.j2')
    result = print_intfs_xmltodict(CONNECTION)
