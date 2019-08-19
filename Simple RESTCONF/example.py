import requests
import urllib3
import json
from jinja2 import Environment, FileSystemLoader
from pprint import pprint

CONNECTION = {
    'host': '192.168.30.22',
    'port': 830,
    'username': 'cisco',
    'password': 'cisco',
    'hostkey_verify': False
}

CONFIG_DATA = {
'interfaces': [
    {'id': '2',
    'description': 'Loopback number one',
    'address': '10.1.1.2',
    'netmask': '255.255.255.0'
    },
    {'id': '3',
    'description': 'Loopback number two',
    'address': '10.1.1.3',
    'netmask': '255.255.255.0'
    }
]
}

# Disable SSL validation warning in requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def config(connection, method, uri, data = False):
    url = 'https://{}/{}'.format(connection['host'], uri)
    headers = {'accept': 'application/vnd.yang.data+json', 'Content-Type': 'application/vnd.yang.data+json'}
    if method == 'post':
        result = requests.post(url, auth=(connection['username'], connection['password']), headers=headers, data=data, verify=False)
    elif method == 'patch':
        result = requests.patch(url, auth=(connection['username'], connection['password']), headers=headers, data=data, verify=False)
    elif method == 'del':
        result = requests.delete(url, auth=(connection['username'], connection['password']), headers=headers, verify=False)
    elif method == 'get':
        result = requests.get(url, auth=(connection['username'], connection['password']), headers=headers, verify=False)
    else:
        print('Please specify the method [post, path, del, get]')
    return result


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
spacer = '+' * 100

# Generate a Loopback json configuration using template. Then pass it to devices with a for loop.
print(spacer)
for interface in CONFIG_DATA['interfaces']:
    print(f'*** Creating a configuration for interface Loopback{interface["id"]}')
    data = cfg_from_template('loopback-template.j2', interface)
    print(data)
    print('*** Send generated configuration to device using "restconf/api/config/interfaces/" and POST method')
    post_result = config(CONNECTION, "post", 'restconf/api/config/interfaces/', data=data)
    print(f'*** Result code: {post_result.status_code} for Loopback{interface["id"]}')
print(spacer)

# Get configuration from device. We should see a couple of newly created loopback interfaces.
print(spacer)
print('*** Get interface information from device using "restconf/api/config/interfaces/" and GET method')
get_result = config(CONNECTION, 'get', 'restconf/api/config/interfaces/')
print(f'*** The result text is:{get_result.text}')
print(spacer)

# Remove newly created loopbacks
print(spacer)
for interface in CONFIG_DATA['interfaces']:
    print('*** Removing Loopbacks with "restconf/api/config/interfaces/interface/LoopbackX" and DEL method')
    del_result = config(CONNECTION, 'del', 'restconf/api/config/interfaces/interface/Loopback{}'.format(interface['id']))
    print(f'*** Status code {del_result.status_code} for Loopback{interface["id"]}')
print(spacer)

# Get interfaces again
print(spacer)
print('Get interfaces from the device again')
get_result = config(CONNECTION, 'get', 'restconf/api/config/interfaces/')
print(f'*** The result text is:{get_result.text}')
print(spacer)

# Json can be easily converted to native Python objects.
print(spacer)
converted_json = json.loads(get_result.text)
interface_list = [interface['name'] for interface in converted_json['ietf-interfaces:interfaces']['interface']]
print(f'*** Now you have only the following interfaces{interface_list}')
print(spacer)

# Changing the hostname with PATCH method
print(spacer)
print('*** Changing hostname using "restconf/api/config/native" and PATCH method')
data = {"ned:native": {"hostname": "R12"}}
print(f'*** Data to be send {data}')
patch_result = config(CONNECTION, 'patch', 'restconf/api/config/native', data=data)
print(spacer)
