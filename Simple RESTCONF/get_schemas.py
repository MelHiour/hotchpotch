import xml.etree.ElementTree as ET
from ncclient import manager

CONNECTION = {
    'host': '192.168.30.22',
    'port': 830,
    'username': 'cisco',
    'password': 'cisco',
    'hostkey_verify': False
}

SCHEMA_LIST = [
    'ned',
    'tailf-common',
    'ietf-inet-types',
    'ietf-yang-types',
    'tailf-meta-extensions',
    'tailf-cli-extensions',
    'ietf-interfaces',
    'ietf-ip'
]

def get_schemas(connection, schema_lists):
    with manager.connect(**connection) as m:
        for schema in schema_lists:
            print(f'** Trying to get {schema}')
            raw_schema = m.get_schema(schema)
            root = ET.fromstring(raw_schema.xml)
            yang_text = list(root)[0].text
            yang_file_name = 'yang_models/'+schema+'.yang'
            with open(yang_file_name, 'w') as file:
                file.write(yang_text)

if __name__ == '__main__':
    get_schemas(CONNECTION, SCHEMA_LIST)
