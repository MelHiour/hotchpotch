#!/usr/bin/python
import time
import re
import os
import requests
import Adafruit_DHT
from datetime import datetime

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=1)
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

    now = datetime.now()
    seg.text = '{first:>4.1f}C{second}'.format(second=now.strftime("%H.%M"), first=temperature)
    time.sleep(2)

    now = datetime.now()
    seg.text = '{first:>4.1f}H{second}'.format(second=now.strftime("%H.%M"), first=humidity)
    time.sleep(2)

    now = datetime.now()
    seg.text = '{first:>3}T{second}'.format(second=now.strftime("%H.%M"), first=outside_temp.group(1))
    time.sleep(2)

    if datetime.timetuple(now)[4] != 0:
        logged = False
    else:
        if not logged:
            filename = '/root/temp-data/'+now.strftime("%d%b%Y")
            if os.path.exists(filename):
                append_write = 'a'
            else:
                append_write = 'w'
            with open(filename, append_write) as file:
                file.write('{} {} {} {}\n'.format(str(now), str(temperature), str(humidity), outside_temp.group(1)))
            logged = True
