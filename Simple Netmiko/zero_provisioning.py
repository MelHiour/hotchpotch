""" Zero day provisioning for EVE-NG devices"""
import yaml
from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler, ssh_exception

def parse_yaml(file):
    """ Parses Yaml and returns Python object
    ARGS:
        file(str) - filename of YAML
    RETURNS:
        inventory - Python object
    """
    with open(file) as inventory_yaml:
        inventory = yaml.load(inventory_yaml, Loader=yaml.FullLoader)
    return inventory

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

def send_cfg_telnet(netmiko_params, config):
    """ Execute a config via telnet
    ARGS:
        netmiko_params(dict) - dictionary with parameters for netmiko
        config(str) - config lines
    RETURNS:
        Result of excecution
    """
    with ConnectHandler(**netmiko_params) as telnet:
        telnet.enable()
        result = telnet.send_config_set(config)
        telnet.save_config()
        return result

def main():
    """ Main function. Parse yaml, for every device prepare a config and send it.
    """
    inventory = parse_yaml('inventory.yaml')
    for device in inventory:
        try:
            print(device['hostname'])
            netmiko_params = {'device_type':'cisco_ios_telnet',
                              'ip': '192.168.0.29',
                              'port': device['oob_port']}
            config = cfg_from_template('base-initial.j2', device)
            print(send_cfg_telnet(netmiko_params, config))
        except (ssh_exception.NetMikoAuthenticationException, ConnectionRefusedError):
            print(f'Device {device["hostname"]} is unreachable')

if __name__ == '__main__':
    main()
