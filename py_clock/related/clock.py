#!/usr/bin/python
import time
import re
import requests
import Adafruit_DHT
import sys
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

    for i in range(8):
        now = datetime.now()
        if i % 2 == 0:
            seg.text = '- ' + now.strftime("%H.%M") + ' -'
        else:
            seg.text = 'o ' + now.strftime("%H%M") + ' o'
        time.sleep(1)
    seg.text = '{0:4.1f}C{1:4.1f}H'.format(temperature, humidity)
    time.sleep(3)
    seg.text = 'OUT {0:>3}C'.format(outside_temp.group(1))
    time.sleep(3)
