import pygal
from pygal.style import DarkSolarizedStyle
import sqlite3

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
        time.append(item[0].split('.')[0])
        inside_temp.append(float(item[1]))
        humidity.append(float(item[2]))
        pressure.append(float(item[3])/10)
        outside_temp.append(float(item[4]))

    line_chart = pygal.Line(x_label_rotation=-45, style=DarkSolarizedStyle)
    line_chart.title = "Weather conditions"
    line_chart.x_labels = time
    line_chart.add('inside_temp', inside_temp)
    line_chart.add('humidity', humidity)
    line_chart.add('pressure*10', pressure)
    line_chart.add('outside_temp', outside_temp)
    line_chart.render_to_file('temp_pygal.svg')

def main():
    tupled_data = get_db_data('/root/temp-data/temp-data.db', 'weather', '2019-02-02', '2019-02-03')
    graph_from_data(tupled_data)

if __name__ == '__main__':
    main()
