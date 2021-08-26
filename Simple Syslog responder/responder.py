import requests
import json
import urllib3
import beanstalkc
from jinja2 import Template

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = 'SECRET_ONE'
SHUT_INTERFACE = '[{"op": "set", "path": ["interfaces", "ethernet", "{{INTERFACE_ID}}", "disable"]}]'
ADD_ADDRESS = '[{"op": "set", "path": ["firewall", "group", "address-group", "BAD_GUYS", "address", "{{ADDRESS}}"]}]'

def prep_config(generated_config, api_key):
    '''
    Creating a dictionary which can be accepted by VyOS
    {'data':(None,DATA),{'key':(None,KEY)}
    '''
    to_push = {}
    to_push['data'] = (None, generated_config.replace('\n',''))
    to_push['key'] = (None, api_key)
    return(to_push)

def post_config(target, to_push):
    url = 'https://' + target + '/configure'
    r = requests.post(url, files=to_push, verify=False)
    return(r)

def save_config(target, api_key):
    url = 'https://' + target + '/config-file'
    data = '{"op": "save"}'
    to_push = prep_config(data, api_key)
    r = requests.post(url, files=to_push, verify=False)
    return(r)

if __name__ == '__main__':
    beanstalk = beanstalkc.Connection(host='localhost', port=11300)
    while True:
        job = beanstalk.reserve()
        task = json.loads(job.body)
        if task['type'] == 'interface_down':
            t = Template(SHUT_INTERFACE)
            config = t.render(INTERFACE_ID = task['interface'])
            print(config)
        elif task['type'] == 'password_failed':
            t = Template(ADD_ADDRESS)
            config = t.render(ADDRESS = task['from'])
            print(config)
        else:
            print('Type not supported')

        prepared_config = prep_config(config, API_KEY)
        r = post_config(task['host'], prepared_config)
        print('\tReturned result is "{}"'.format(r.text))

        print('\tSaving configuration...')
        r = save_config(task['host'], API_KEY)
        print('\tReturned result is "{}"'.format(r.text))
