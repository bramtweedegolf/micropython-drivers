from th02 import TH02
import time

# Connect Grove TH02 to I2C1

# Setup sensor
sensor = TH02()

# Read temperature and humidity
# every 60 seconds
while True:
  temp = sensor.read_temp()
  hum = sensor.read_hum()
  print(hum, temp)
  time.sleep(60)
