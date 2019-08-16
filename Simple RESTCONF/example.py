import requests
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

def config(connection, method, uri, data = False):
    url = 'https://{}/{}'.format(connection['host'], uri)
    headers = {'accept': 'application/vnd.yang.data+json', 'Content-Type': 'application/vnd.yang.data+json'}
    if method == 'post':
        result = requests.post(url, auth=(connection['username'], connection['password']), headers=headers, data=data, verify=False)
    elif method == 'patch':
        result = requests.patch(url, auth=(connection['username'], connection['password']), headers=headers, data=data, verify=False)
    elif method == 'del':
        result = requests.delete(url, auth=(connection['username'], connection['password']), headers=headers, verify=False)
    else:
        print('Please specify the method [post, path, del]')
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

def main():
    for interface in CONFIG_DATA['interfaces']:
        data = cfg_from_template('loopback-template.j2', interface)
        print(data)
        result = config(CONNECTION, "post", 'restconf/api/config/interfaces/', data=data)
        print(result.status_code, result.text)

if __name__ == '__main__':
    main()
