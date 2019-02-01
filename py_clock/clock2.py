#!/usr/bin/python
import time
import re
import sqlite3
import requests
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085
from datetime import datetime

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=1)
sensor = BMP085.BMP085()
seg = sevensegment(device)

seg.text = 'LOVECECA'
for x in range(5):
    for intensity in range(16):
        seg.device.contrast(intensity * 16)
        time.sleep(0.1)

device.contrast(0x7F)
seg.device.contrast(16)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
    r = requests.get('http://wttr.in/?format=3')
    outside_temp = re.search(' (-?\d{1,2})', r.text)
    pressure = sensor.read_pressure()*0.0075006157584566

    now = datetime.now()
    seg.text = '{first:>4.1f}C{second}'.format(second=now.strftime("%H.%M"), first=temperature)
    time.sleep(2)

    now = datetime.now()
    seg.text = '{first:>4.1f}H{second}'.format(second=now.strftime("%H.%M"), first=humidity)
    time.sleep(2)

    now = datetime.now()
    seg.text = '{first:>3}P{second}'.format(second=now.strftime("%H.%M"), first=int(pressure))
    time.sleep(2)

    now = datetime.now()
    seg.text = '{first:>3}T{second}'.format(second=now.strftime("%H.%M"), first=outside_temp.group(1))
    time.sleep(2)

    if datetime.timetuple(now)[4] != 14:
        logged = False
    else:
        if not logged:
            query = 'INSERT into weather values (?, ?, ?, ?, ?)'
            data = (str(now), str(temperature), str(humidity), str(pressure), outside_temp.group(1))
            with sqlite3.connect('/root/temp-data/temp-data.db') as connector:
                connector.execute(query, data)
            logged = True
