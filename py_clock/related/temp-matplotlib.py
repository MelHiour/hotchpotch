import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as dates

time = []
inside_temp = []
humidity = []
outside_temp = []

with open('/root/temp-data') as file:
    for line in file.readlines():
        time.append(dates.datestr2num('{} {}'.format(line.split(' ')[0], line.split(' ')[1])))
        inside_temp.append(line.split(' ')[2])
        humidity.append(line.split(' ')[3])
        outside_temp.append(line.strip().split(' ')[4])

plt.plot_date(time, inside_temp, '-', label='inside')
plt.plot_date(time, humidity, '-', label='humidity')
plt.plot_date(time, outside_temp, '-', label='outside')
plt.legend(loc='upper left')
plt.grid(True)
plt.savefig('temp_matplotlib_result.png')
