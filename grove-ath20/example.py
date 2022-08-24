from ath20 import ATH20
import time

# Connect Grove ATH20 to I2C0

# Setup sensor
sensor = ATH20()

# Read temperature and humidity
# every 60 seconds
while True:
  (hum, temp) = sensor.measure()
  print(hum, temp)
  time.sleep(60)
