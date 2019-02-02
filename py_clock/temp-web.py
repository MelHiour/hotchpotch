import pygal
import sqlite3
from flask import Flask

def get_db_data(db_path, table_name, from_date, until_date):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute("select * from {} where date between '{}' and '{}'".format(table_name, from_date, until_date))
        result = cursor.fetchall()
    return result

def graph_from_data(data):
    time = []
    inside_temp = []
    humidity = []
    pressure = []
    outside_temp = []

    for item in data:
        time.append(item[1])
        inside_temp.append(item[2])
        humidity.append(item[3])
        pressure.append(item[4])
        outside_temp.append(item[5])

    line_chart = pygal.Line(x_label_rotation=-45)
    line_chart.title = "Weather conditions"
    line_chart.x_labels = time
    line_chart.add('inside_temp', inside_temp)
    line_chart.add('humidity', humidity)
    line_chart.add('pressure', humidity)
    line_chart.add('outside_temp', outside_temp)
    line_chart.render_to_file('temp_pygal.svg')

def main():
    tupled_data = get_db_data('/root/temp-data/temp-data.db', 'weather', '2019-02-01', '2019-02-02')
    graph_from_data(tupled_data)

'''
app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello!'
'''
if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True)
    main()
