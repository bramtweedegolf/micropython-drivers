#
# http://docs.micropython.org/en/v1.9.3/esp8266/esp8266/quickref.html#onewire-driver
#

import time, ds18x20
ds = ds18x20.DS18X20(ow)
roms = ds.scan()
ds.convert_temp()
time.sleep_ms(750)
for rom in roms:
    print(ds.read_temp(rom))
