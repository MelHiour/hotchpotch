import pygal

time = []
inside_temp = []
humidity = []
outside_temp = []

with open('/root/temp-data') as file:
    for line in file.readlines():
        time.append('{} {}'.format(line.split(' ')[0], line.split(' ')[1].split('.')[0]))
        inside_temp.append(float(line.split(' ')[2]))
        humidity.append(float(line.split(' ')[3]))
        outside_temp.append(float(line.strip().split(' ')[4]))

line_chart = pygal.Line(x_label_rotation=-45)
line_chart.title = "Conditions"
line_chart.x_labels = time
line_chart.add('inside', inside_temp)
line_chart.add('humidity', humidity)
line_chart.add('outside', outside_temp)
line_chart.render_to_file('temp_pygal.svg')
