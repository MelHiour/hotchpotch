# Super simple API based on Mastering Python Networking by Eric Chou
'''
It accepts the folowing URLs:
    /devices/
        GET     Returns a list of URLs for every Device
        POST    Accepts a json-encoded body. Returns a URL for newly created device.

                Body {
                "hostname": "TEST",
                "mgmt_ip": "192.168.30.50",
                "role": "router",
                "vendor": "cisco",
                "os": "15.4"
                }

    /devices/<int:id>
        GET     Returns a json with device information
        PUT     Accepts a json-encoded body. Modify existing device

    /devices/<int:id>/interfaces
        GET     Returns a json with all interfaces (using get_interfaces NAPALM getter)
        POST    Accepts a json-encoded body. Allows to control a OpStatus of interface. Returns a diff just for giggles...
                Body {
                "interface": "Ethernet0/3",
                "state": "down"
                }

    /devices/<int:id>/sysinfo
        GET     Returns a system info for particular device (using get_facts NAPALM getter)
'''

from flask import Flask, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth
from network_modules import show_interfaces, show_sys, interface_oper

# Initiate Flask app, db and auth
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class ValidationError(ValueError):
    pass

# User class with set_password and get_password methods
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# Device class with get_url, export_data, import_data methods
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

# Start auth decorator
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    return user.verify_password(password)

@app.before_request
@auth.login_required
def before_request():
    pass

# from HTTPAuath extension
@auth.error_handler
def unathorized():
    response = jsonify({'status': 401, 'error': 'unahtorized',
                        'message': 'please authenticate'})
    response.status_code = 401
    return response

@app.route('/devices/', methods=['GET'])
def get_devices():
    return jsonify({'devices': [device.get_url()
                               for device in Device.query.all()]})

@app.route('/devices/<int:id>', methods=['GET'])
def get_device(id):
    return jsonify(Device.query.get_or_404(id).export_data())

@app.route('/devices/', methods=['POST'])
def new_device():
    device = Device()
    device.import_data(request.json)
    db.session.add(device)
    db.session.commit()
    return jsonify({}), 201, {'Location': device.get_url()}

@app.route('/devices/<int:id>', methods=['PUT'])
def edit_device(id):
    device = Device.query.get_or_404(id)
    device.import_data(request.json)
    db.session.add(device)
    db.session.commit()
    return request.json

@app.route('/devices/<int:id>/interfaces', methods=['GET','POST'])
def interface_interaction(id):
    device = Device.query.get_or_404(id).export_data()
    if request.method == 'GET':
        return show_interfaces(device['mgmt_ip'])
    elif request.method == 'POST':
        ip = device['mgmt_ip']
        config = request.json
        difference = interface_oper(ip, config['interface'], config['state'])
        return jsonify({'diff': difference})
    else:
        return 405

@app.route('/devices/<int:id>/sysinfo', methods=['GET'])
def get_sys(id):
    device = Device.query.get_or_404(id).export_data()
    return show_sys(device['mgmt_ip'])

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
