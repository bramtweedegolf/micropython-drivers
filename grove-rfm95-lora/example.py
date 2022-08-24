# main.py -- put your code here!

import lib
import time

ll = lib.getLL()

while True:
  ll.sendText('Hello world')
  time.sleep(60)
