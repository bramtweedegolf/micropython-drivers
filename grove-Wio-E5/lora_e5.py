from pyb import UART
from pyb import delay

class Lora:

  uart = None
  joined = False

  def __init__(self, port = 3):
    self.uart = UART(port, 9600)

  def test(self):
    result = self.send('AT')
    return result == ['+AT: OK']

  def setup(self):
    result = self.send('AT+MODE=LWOTAA')
    print(result)
    result = self.send('AT+LOG=DEBUG')
    print(result)
    result = self.send('AT+DR=3')
    print(result)
    result = self.send('AT+LW=VER,V103')
    print(result)

  def join(self, debug = False):
    self.uart.write("AT+JOIN\r\n")
    result = self.read_input(15000)
    if '+JOIN: Join failed' in result:
      self.joined = False
      print('fail')
    if '+JOIN: Network joined' in result:
      self.joined = True
      print('success')
    if '+JOIN: Joined already' in result:
      self.joined = True
      print('success')
    if debug:
      print(result)

  def read_input(self, timeout):
    result = []
    while timeout > 0:
      timeout -= 100
      delay(100)
      if self.uart.any:
        r = self.uart.read()
        if r:
          result.append(r.decode())
    merged = "".join(result)
    lines = merged.split("\r\n")
    res = []
    for line in lines:
      if not(line == ""):
        res.append(line)
    return res

  def send(self, cmd, dly = 500):
    length = self.uart.write(cmd + "\r\n")
    delay(dly)
    result = self.uart.read()
    if result:
      lines = result.split("\r\n")
      return lines[:-1]
    else:
      return ['No result']

  def message(self, message):
    self.uart.write("AT+MSG=\"" + message + "\"\r\n")
    result = self.read_input(15000)
    print(result)

