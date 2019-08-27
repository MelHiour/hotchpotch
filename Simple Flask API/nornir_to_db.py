import yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), unique=True)
    mgmt_ip = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(64))

    def get_url(self):
        return url_for('get_device', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'hostname': self.hostname,
            'mgmt_ip': self.mgmt_ip,
            'role': self.role
        }

    def import_data(self, data):
        try:
            self.hostname = data['hostname']
            self.mgmt_ip = data['mgmt_ip']
            self.role = data['role']
        except KeyError as e:
            raise ValidationError('Invalid device: missing ' + e.args[0])
        return self

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

def hosts_to_dict(device, host_data):
    result = {}
    result['hostname'] = device
    result['mgmt_ip'] = host_data['hostname']
    result['role'] = host_data['data']['type']
    return result

if __name__ == '__main__':
    db.create_all()
    nornir_inventory = parse_yaml('hosts.yaml')
    for host, data in nornir_inventory.items():
        device_data = hosts_to_dict(host, data)
        device = Device()
        device.import_data(device_data)
        db.session.add(device)
        db.session.commit()
