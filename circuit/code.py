"""
code.py
(c) C.A. Little
Rev 1.0, August 8 2019
MIT License

Read temperature from DS12B20/DS18B20 and upload to data endpoint via HTTP.

Requires 
Adafruit CircuitPython OneWire library (for managing the one-wire bus)
Adafruit CircuitPython DS18X20 library (for decoding data from temp sensor)
Adafruit CircuitPython ESP32SPI libraries (for Wifi connectivity)
"""
import time
import board
from adafruit_onewire.bus import OneWireBus
import adafruit_ds18x20
import busio
import neopixel
from digitalio import DigitalInOut
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_requests as requests

def getDevice():
	# notice here we are using digital input 2. If you didnt' wire
	# up to this input, modify the code.
    owb = OneWireBus(board.D2)
    devices = owb.scan()
    for device in devices:
        idString = "ROM = {} \tFamily = 0x{:02x}".format([hex(i) for i in device.rom], device.family_code)
        if idString == "ROM = ['0x28', '0xaa', '0x81', '0x2', '0x38', '0x14', '0x1', '0xfe'] 	Family = 0x28" :
            ds18b20 = adafruit_ds18x20.DS18X20( owb, device)
            ds18b20.resolution = 12
            return ds18b20
    return None
def doGetTemp( ts ) :
    try:
        dc = ts.temperature
        df = (dc * 9/5) + 32
        print('Temperature: %sC / %sF' % ( dc, df ))
        return df
    except:
        print("Something didn't work")

# Set up the temp sensor
ts = getDevice()
if ts is None :
    print ('Error getting bus device temperature.')
    exit(0)
else :
    print ('Temp setup ready.')

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)

wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

while True:
    try:
        print("Posting data...", end='')
        feed = 'tsfeed'
        payload = {'value': doGetTemp( ts ) }
        response = wifi.post(
            "https://io.adafruit.com/api/v2/"+secrets['aio_username']+"/feeds/"+feed+"/data",
            json=payload,
            headers={"X-AIO-KEY":secrets['aio_key']})
        print(response.json())
        response.close()
        print("OK")
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue
    response = None
    # modify this value to determine how long the sleep cycle should be.
    # Probably needs to update every hour, but need to look into 
    # sleep cycling of the ESP32 Wifi connection, since THAT is
    # the major power drain.
    time.sleep(3600)