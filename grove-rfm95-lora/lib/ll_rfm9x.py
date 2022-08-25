"""
    RFM95 / 98 / 99 LinkLayer

    includes basic rx/tx stuff and init

    translated almost 1-to-1
    from https://github.com/erazor83/pyRFM
"""

from pyb import delay

RFM_REG_OP_MODE = const(0x01)
RFM_REG_FRF_MSB = const(0x06)
RFM_REG_FRF_MID = const(0x07)
RFM_REG_FRF_LSB = const(0x08)
RFM_REG_VERSION = const(0x42)
RFM_REG_FIFO_TX_BASE_ADDR = const(0x0e)
RFM_REG_DIO_MAPPING1 = const(0x40)
RFM_REG_PREAMBLE_MSB = const(0x20)
RFM_REG_PREAMBLE_LSB = const(0x21)
RFM_REG_IRQ_FLAGS = const(0x12)
RFM_REG_RX_NB_BYTES = const(0x13)
RFM_REG_FIFO_ADDR_PTR = const(0x0d)
RFM_REG_FIFO_RX_CURRENT_ADDR = const(0x10)
RFM_REG_FIFO_RX_BASE_ADDR = const(0x0f)

RFM_REG_MODEM_CONFIG1 = const(0x1d)
RFM_REG_MODEM_CONFIG2 = const(0x1e)
RFM_REG_MODEM_CONFIG3 = const(0x26)

RFM_REG_FIFO = const(0x00)
RFM_REG_PKT_RSSI_VALUE = const(0x1a)
RFM_REG_PA_CONFIG = const(0x09)
RFM_REG_PA_DAC = const(0x4d)

RFM_MODE_SLEEP = const(0x00)
RFM_MODE_LONG_RANGE = const(0x80)
RFM_MODE_STDBY = const(0x01)
RFM_MODE_TX = const(0x03)
RFM_MODE_RXCONTINUOUS = const(0x05)
RFM_MODE_FSTX = const(0x02)
RFM_MODE_FSRX = const(0x04)

RFM_MAX_POWER = const(0x70)
RFM_PA_DAC_ENABLE = const(0x07)
RFM_PA_DAC_DISABLE = const(0x04)
RFM_PA_SELECT = const(0x80)

RFM_IF_RX_TIMEOUT = const(0x80)
RFM_IF_PAYLOAD_CRC_ERROR = const(0x20)
RFM_IF_RX_DONE = const(0x40)
RFM_IF_CAD_DONE = const(0x04)
RFM_IF_TX_DONE = const(0x08)

RFM_HEADER_LEN = const(4)
RFM_FIFO_SIZE = const(255)
RFM_REG_PAYLOAD_LENGTH = const(0x22)

RFM_FXOSC = 32000000.0
RFM_FSTEP = (RFM_FXOSC / 524288)

class LinkLayer():
  _RX_Buffer = None
  _TX_id = 0
  State = None
  Mode = None
  PL = None

  def __init__(self, pl):
    self.PL = pl
    self.PL.setIRQH(self._handleIRQ)
    self.postInit()

  def readRegister(self, addr):
    if self.PL:
      self.PL.flush()
      self.PL.write([addr,0])
      rx = self.PL.read(2)
      return rx[1]

  def writeRegister(self,addr,val):
    if self.PL:
      addr = addr | RFM_WRITE_REGISTER_MASK
      self.PL.flush()
      self.PL.write([addr,val])

  def _handleIRQ(self):
    pass

  def postInit(self):
    self.flush()
    self.State = {'RX_ok': 0, 'RX_fail': 0, 'TX_ok': 0, 'RSSI': None}

  def getVersion(self):
    return self.PL.readRegister(RFM_REG_VERSION)

  def getOpMode(self):
    return self.PL.readRegister(RFM_REG_OP_MODE)

  def setFiFo(self, tx = 0, rx = 0):
    self.PL.writeRegister(RFM_REG_FIFO_TX_BASE_ADDR, tx)
    self.PL.writeRegister(RFM_REG_FIFO_RX_BASE_ADDR, rx)

  def setOpMode(self, mode, check = False):
    self.Mode = mode
    self.PL.writeRegister(RFM_REG_OP_MODE, mode)
    if check:
      mode = mode
      timeout = 500
      waited = 0
      while waited < timeout:
        cMode = self.getOpMode()
        if cMode == mode:
          return True
        waited += 10
        delay(10)
      return False

  def setOpModeSleep(self, lora=False, check=False):
    if lora:
      return self.setOpMode(RFM_MODE_SLEEP|RFM_MODE_LONG_RANGE, check)
    else:
      return self.setOpMode(RFM_MODE_SLEEP, check)

  def setOpModeIdle(self, check=False):
    return self.setOpMode(RFM_MODE_STDBY, check)

  def setOpModeTx(self,check=False):
    ret = self.setOpMode(RFM_MODE_TX, check)
    self.PL.writeRegister(RFM_REG_DIO_MAPPING1, 0x40)
    return ret

  def setOpModeRx(self,check=False):
    ret = self.setOpMode(RFM_MODE_RXCONTINUOUS, check)
    self.PL.writeRegister(RFM_REG_DIO_MAPPING1, 0x00)
    return ret

  def setModemRegisters(self):
    self.PL.writeRegister(RFM_REG_MODEM_CONFIG1, 0x72)
    self.PL.writeRegister(RFM_REG_MODEM_CONFIG2, 0x74)
    self.PL.writeRegister(RFM_REG_MODEM_CONFIG3, 0x00)

  def setModemConfig(self):
    self.setModemRegisters()

  def setPreambleLength(self,length):
    self.PL.writeRegister(RFM_REG_PREAMBLE_MSB, length >> 8);
    self.PL.writeRegister(RFM_REG_PREAMBLE_LSB, length & 0xff);

  def setFrequency(self,freq):
    frf = int( (freq * 1000000.0) / RFM_FSTEP )
    self.PL.writeRegister(RFM_REG_FRF_MSB, (frf >> 16) & 0xff)
    self.PL.writeRegister(RFM_REG_FRF_MID, (frf >> 8) & 0xff)
    self.PL.writeRegister(RFM_REG_FRF_LSB, frf & 0xff)

  def setTxPower(self,power,useRFO=False):
    if (useRFO):
      if (power > 14):
        power = 14
      elif (power < -1):
        power = -1
        self.PL.writeRegister(RFM_REG_PA_CONFIG, RFM_MAX_POWER | (power + 1))
    else:
      if (power > 23):
        power = 23
      elif (power < 5):
        power = 5
      if (power > 20):
        self.PL.writeRegister(RFM_REG_PA_DAC, RFM_PA_DAC_ENABLE)
        power = power - 3
      else:
        self.PL.writeRegister(RFM_REG_PA_DAC, RFM_PA_DAC_DISABLE)
    self.PL.writeRegister(RFM_REG_PA_CONFIG, RFM_PA_SELECT | (power-5))

  def _handleIRQ(self):
    irq_flags = self.PL.readRegister(RFM_REG_IRQ_FLAGS)
    if (self.Mode & RFM_MODE_FSRX) and (irq_flags&(RFM_IF_RX_TIMEOUT|RFM_IF_PAYLOAD_CRC_ERROR)):
      self.State['RX_fail'] = self.State['RX_fail'] + 1
    if (self.Mode & RFM_MODE_FSRX) and (irq_flags & RFM_IF_RX_DONE):
      length = self.PL.readRegister(RFM_REG_RX_NB_BYTES)
      self.PL.writeRegister(RFM_REG_FIFO_ADDR_PTR, self.PL.readRegister(RFM_REG_FIFO_RX_CURRENT_ADDR))
      buf = self.PL.readRegister(RFM_REG_FIFO, length)
      self._RX_Buffer = self._RX_Buffer + buf
      self.PL.writeRegister(RFM_REG_IRQ_FLAGS, 0xff)
      self.State['RSSI'] = self.PL.readRegister(RFM_REG_PKT_RSSI_VALUE) - 137
    elif (self.Mode & RFM_MODE_FSRX) and (irq_flags & RFM_IF_CAD_DONE):
      print('IRQ / rx CAD done')
    elif (self.Mode & RFM_MODE_FSTX) and (irq_flags & RFM_IF_TX_DONE):
      self.State['TX_ok'] = self.State['TX_ok']+1
      self.setOpModeIdle()
    self.PL.writeRegister(RFM_REG_IRQ_FLAGS, 0xff)
    if (self.Mode & RFM_MODE_FSRX):
      self.setOpModeRx()

  def waitPacketSent(self, timeout = 1):
    timeout = timeout * 1000
    waited = 0
    while waited < timeout:
      self.PL.checkIRQ()
      if not (self.Mode & RFM_MODE_FSTX):
        return True
      delay(10)
      waited += 10
    return False

  def waitRX(self, timeout = None):
    self.setOpModeRx()
    if timeout == None:
      while True:
        self.PL.checkIRQ()
        if len(self._RX_Buffer):
          return True
    else:
      timeout = timeout * 1000
      waited = 0
      while waited < timeout:
        self.PL.checkIRQ()
        if len(self._RX_Buffer):
          return True
        delay(10)
        waited += 10

  def available(self):
    self.PL.checkIRQ()
    print('available', len(self._RX_Buffer))
    return len(self._RX_Buffer)

  def recv(self,length=None,timeout=None):
    if length==None:
      self.waitRX(timeout)
    elif timeout:
      timeout = timeout * 1000
      waited = 0
      while waited < timeout:
        if self.available() >= length:
          return self._RX_Buffer[0:length]
        else:
          while True:
           if self.available()>=length:
             return self._RX_Buffer[0:length]
        delay(10)
        waited += 10
    ret = self._RX_Buffer
    self._RX_Buffer = []
    return ret

  def flush(self):
    self._RX_Buffer = []

  def sendText(self, text):
    return self.send(bytes(text, "iso-8859-1"))

  def sendByteArray(self, data):
    return self.send(data)

  def send(self, data):
    if self.waitPacketSent():
      self.setOpModeIdle()

      # Position at the start of fifo
      self.PL.writeRegister(RFM_REG_FIFO_ADDR_PTR, 0)

      # The header
      #print('header')
      self.PL.writeRegister(RFM_REG_FIFO, [0,0,self._TX_id,0])

      # The message
      #print('message')
      length = len(data) + RFM_HEADER_LEN
      self.PL.writeRegister(RFM_REG_FIFO, data);
      self.PL.writeRegister(RFM_REG_PAYLOAD_LENGTH, length)

      # Transmit
      #print('transmit')
      self._TX_id = (self._TX_id + 1)&0xff
      self.setOpModeTx()

      print('sent', data, length)
