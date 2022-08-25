# main.py -- put your code here!

from grove_gps import GPS
from lora_e5 import Lora

import time

gps = GPS()
l = Lora()

while True:
  if not l.joined:
    l.join()
  if l.joined:
    loc = gps.location()
    l.message(loc)
  time.sleep(30)