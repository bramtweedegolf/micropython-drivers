#
# TH02
#
# i2c.scan()
# i2c.is_ready(64)
#
# https://docs.micropython.org
#

from pyb import I2C

READY_REGISTER = const(0)
CONFIG_REGISTER = const(3)
DEV_ADDRESS = const(64)
ID_REGISTER = const(0x11)

class TH02:

  i2c = None

  def __init__(self):
    self.i2c = I2C(1, I2C.MASTER)
    devs = self.i2c.scan()
    if not DEV_ADDRESS in devs:
      print('Error: device not found')

  def ready(self):
    if (self.i2c == None):
      return False
    return self.i2c.mem_read(1, DEV_ADDRESS, READY_REGISTER) == b'\x00'

  def read_device_id(self):
    if (self.i2c == None):
      return False
    return self.i2c.mem_read(1, DEV_ADDRESS, ID_REGISTER)

  def read_temp(self):
    self.i2c.mem_write(0x11, DEV_ADDRESS, CONFIG_REGISTER)
    while not(self.ready()):
      pass
    low = self.i2c.mem_read(8, DEV_ADDRESS, 2)
    high = self.i2c.mem_read(8, DEV_ADDRESS, 1)
    data = (high[0] << 8) | low[0]
    temp = ((data >> 2) / 32.0) - 50.0
    return temp

  def read_hum(self):
    self.i2c.mem_write(0x01, DEV_ADDRESS, CONFIG_REGISTER)
    while not(self.ready()):
      pass
    low = self.i2c.mem_read(8, DEV_ADDRESS, 2)
    high = self.i2c.mem_read(8, DEV_ADDRESS, 1)
    data = (high[0] << 8) | low[0]
    hum = ((data >> 4) / 16.0) - 24.0
    return hum
