from flask import Flask, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

class ValidationError(ValueError):
    pass

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

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)
