#!/usr/bin/python
import time
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
time.sleep(2)

seg.device.contrast(16)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
    for i in range(8):
        now = datetime.now()
        if i % 2 == 0:
            seg.text = '- ' + now.strftime("%H.%M") + ' -'
        else:
            seg.text = 'o ' + now.strftime("%H%M") + ' o'
        time.sleep(1)
    seg.text = '{0:4.1f}C{1:4.1f}H'.format(temperature, humidity)
    time.sleep(3)
