#
# Grove GPS (Sim 28)
#
# https://docs.micropython.org
#

from pyb import UART

#ID_REGISTER = const(0x11)

class GPS:

  uart = None

  def __init__(self, port = 1):
    self.uart = UART(port, 9600)

  def available(self):
    return self.uart.any() > 0

  def is_packet(self, string):
    return string[:6] == '$GPGGA'

  def location(self):
    data = self.read()
    if data and not data['long']:
      return "No signal"
    string = str(float(data['lat']) / 100.0) + "," + str(float(data['long']) / 100.0)
    return string

  def parse(self, bits):
    return {
      'time': bits[1],
      'lat' : bits[2],
      'lat_ns' : bits[3],
      'long' : bits[4],
      'long_ew': bits[5],
      'fix': bits[6],
      'sats': bits[7],
      'alt': bits[9]
    }

  def read_string(self):
   if not self.available():
     return None
   data = self.uart.read()
   if not data:
     return None
   try:
     return data.decode()
   except:
     return None

  def split_string(self, string):
    if "\r\n" in string:
      lines = string.split("\r\n")
      for line in lines:
        if self.is_packet(line):
          return line.split(",")
    else:
      return string.split(",")
    return None

  def read(self):
    if self.available():
      string = self.read_string()
      while (not string) or (not self.is_packet(string)):
        string = self.read_string()
      return self.parse(self.split_string(string))
    return None
