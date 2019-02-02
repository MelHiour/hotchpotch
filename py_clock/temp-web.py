import sqlite3
from flask import Flask

def get_db_data(db_path, table_name):
    with sqlite3.connect(db_path) as connection:
        result = connection.fetchall('select * from {}'.format(table_name))
    return result
'''
app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello!'
'''
if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True)
    result = get_db_data('/root/temp-data/temp-data.db', 'weather')
