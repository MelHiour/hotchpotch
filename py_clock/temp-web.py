import sqlite3
from flask import Flask

def get_db_data(db_path, table_name, from_date, until_date):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute("select * from {} where date between '{}' and '{}'".format(table_name, from_date, until_date))
        result = cursor.fetchall()
    return result
'''
app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello!'
'''
if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True)
    result = get_db_data('/root/temp-data/temp-data.db', 'weather', '2019-02-01', '2019-02-02')
    print(result)
