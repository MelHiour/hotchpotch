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

while True:
    for i in range(5):
        now = datetime.now()
        if i % 2 == 0:
            seg.text = '- ' + now.strftime("%H.%M") + ' -'
        else:
            seg.text = '- ' + now.strftime("%H%M") + ' -'
        time.sleep(1)
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
    seg.text = '{0:0.1f}C {1:0.1f}H'.format(temperature, humidity)
    time.sleep(5)
