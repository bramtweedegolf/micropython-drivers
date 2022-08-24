from machine import I2C, lightsleep

STATUS_COMMAND = const(0x71)
TRIGGER_MEASUREMENT = const(0xAC)
CALIBRATE_COMMAND = const(0xBE)
STATUS_REGISTER = const(0x38)
DEV_ADDRESS = const(0x38) # 56

# TODO: Better error handling
# TODO: Implement CRC check
# TODO: Param for I2C bus

class ATH20:

  i2c = None

  # Init the I2C
  def __init__(self):
    self.i2c = I2C(0)
    devices = self.i2c.scan()
    if not DEV_ADDRESS in devices:
      print('Error: device not found')
      exit()
    lightsleep(40) # Wait 40ms after powerup

  # Read status word
  def getStatus(self):
    byte = self.i2c.readfrom_mem(DEV_ADDRESS, STATUS_REGISTER, 1)
    byte = ord(byte) + 256
    byte = bin(byte)[3:]
    return byte

  # Calibrate the sensor if needed
  def calibrate(self):
    self.i2c.writeto_mem(DEV_ADDRESS, CALIBRATE_COMMAND, bytes([0x08, 0x00]))
    lightsheep(10) # Wait for 10ms

  # Check if sensor is calibrated.
  def isCalibrated(self):
    byte = self.getStatus()
    return byte[3] == '1'

  # Check if a measurement if ready
  def isReady(self):
    byte = self.getStatus()
    return byte[7] == '0'

  # Turn the given byte into a bit array
  def process(self, byte):
    data = bin(byte)[2:]
    while (len(data) < 8):
      data = '0' + data
    return data

  # Calculate the relative humidity %
  def calculateHumidity(self, value):
      return (value / pow(2, 20)) * 100

  # Calculate the temperate in C
  def calculateTemperature(self, value):
      return (value / pow(2, 20)) * 200 - 50

  # Take a measurement
  def measure(self):

    if not self.isCalibrated():
      self.calibrate()

    if not self.isCalibrated():
      print('Error: could not calibrate')
      exit()

    self.i2c.writeto_mem(DEV_ADDRESS, TRIGGER_MEASUREMENT, bytes([0x33, 0x00]))
    lightsleep(80)

    while not(isReady()):
      lightsleep(80)

    # The result is in 6 bytes
    # Note: we ignore the CRC check for now
    return i2c.readfrom(DEV_ADDRESS, 6)

  # Attempt to read temp and humidity
  def read(self):
    results = self.measure()

    # Collect the humidity bits
    hum = ""
    hum += self.process(results[1])
    hum += self.process(results[2])
    hum += self.process(results[3])[0:4]

    # Collect the temp bits
    temp = ""
    temp += self.process(results[3])[4:]
    temp += self.process(results[4])
    temp += self.process(results[5])

    hum = self.calculateHumidity(int(hum, 2))
    temp = self.calculateTemperature(int(temp, 2))

    print(hum, temp)
    return (hum, temp)

