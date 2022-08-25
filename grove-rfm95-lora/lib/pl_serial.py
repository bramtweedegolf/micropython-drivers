from pyb import UART

class Serial():

  isOpen = False
  uart = None

  def setIRQH(self, callback):
    self._IRQH = callback

  def open(self):
    if not self.isOpen:
      self.uart = UART(3, 57600)
      self.uart.init(57600,  timeout=500)
      self.isOpen = True
    else:
      pass

  def write(self, cmd, reg, length=None, data=None):
    if not self.isOpen:
      self.open()
    if self.isOpen:
      if data != None:
        if type(data) == bytes:
          length=len(data)
          newdata = [cmd, reg, length]
          for i in data:
            newdata.append(i)
          data = newdata
        else:
          length=len(data)
          data=[cmd,reg,length]+data
      else:
        data=[cmd,reg,length]
      #print(data)
      buff = bytearray(data)
      if (self.uart.write(buff) == None):
        print('Write timeout')

  def read(self, length):
    if not self.isOpen:
      self.open()
    if self.isOpen:
      data = self.uart.read(length)
      return data

  def readRegister(self, addr, length = 1):
    self.write(82, addr, length)
    rx = self.read(length)
    if length == 1:
      return rx[0]
    else:
      return rx

  def writeRegister(self, addr, val):
    addr = addr | 1<<7
    if type(val) == int:
      self.write(87, addr, None, [val])
    elif type(val)==list:
      self.write(87, addr, None, val)
    elif type(val)==bytes:
      self.write(87, addr, None, val)

  def checkIRQ(self):
    if not self.isOpen:
      self.open()
    if self.isOpen:
      if self.uart.any():
        data = self.read(self.uart.any())
        if (data[0] == 73) and self._IRQH:
          self._IRQH()
