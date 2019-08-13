"""
code.py
(c) C.A. Little
Rev 1.0, August 8 2019
Shared under MIT License

Read temperature from DS12B20/DS18B20 and upload to data endpoint via HTTP.

Requires 
    Adafruit CircuitPython OneWire library (for managing the one-wire bus)
    Adafruit CircuitPython DS18X20 library (for decoding data from temp sensor)
    Adafruit CircuitPython ESP32SPI libraries (for Wifi connectivity)
"""
import time
import board
import busio
import neopixel
import adafruit_ds18x20
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
from adafruit_onewire.bus import OneWireBus
# These two aren't used, but keeping them here for "later"
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket


def getDevice():
	# This function is used to query the OneWireBus (OWB) to grab a list
    # of devices. This function expects that the sensor is wired up to 
    # Digital pin 2. If you used a different pin, change the following
    # line of code:
    owb = OneWireBus(board.D2)

    devices = owb.scan()
    for device in devices:

        idString = "ROM = {} \tFamily = 0x{:02x}".format([hex(i) for i in device.rom], device.family_code)
        #
        # This is the particular sensor identification string returned by the DS18B20 that I am using.
        # You might have to modify this string if it doesn't work for you. You can log output to Mu serial console
        # to see the idStrings for all your OneWire devices. 
        # e.g. 
        # print idString
        if idString == "ROM = ['0x28', '0xaa', '0x81', '0x2', '0x38', '0x14', '0x1', '0xfe'] 	Family = 0x28" :
            ds18b20 = adafruit_ds18x20.DS18X20( owb, device)
            #
            # There are several resolution settings (e.g. how many significant digits of temperature are sent)
            # The settings are 9,10,11,12. Just FYI, the larger the resolution, the longer the time to generate
            # the data (we're talking 100-700ms) but for our purposes I would rather have ALL THE SIGNIFICANT DIGITS!
            # See here for more info: https://www.maximintegrated.com/en/app-notes/index.mvp/id/4377 or https://cdn-shop.adafruit.com/datasheets/DS18B20.pdf
            # So, 12 it is. :-)
            ds18b20.resolution = 12
            return ds18b20
    return None
def doGetTemp( ts ) :
    #
    # This function expects the temp sensor object to be passed in,
    # and it returns the temperature reading in Farenheit because
    # America can't be bothered to using metric for anything ::eyeroll::
    #
    try:
        dc = ts.temperature
        df = (dc * 9/5) + 32
        print('Temperature: %sC / %sF' % ( dc, df ))
        return df
    except:
        print("Something didn't work")

##################################
#   Main Function
##################################
#
# Set up the temp sensor by obtaining the OneWireBus address for the temp sensor.
#
ts = getDevice()
#
# Make sure we have a valid device.
#
if ts is None :
    print ('Error getting bus device temperature.')
    exit(0)
else :
    print ('Temp setup ready.')

#
# Load the wifi connection information and AIO bits.
#
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

#
# Set up the Wifi components and the all-important NeoPixel!
#
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

#
# Finally, start the while loop that goes on ...FOR EVERever ever ver ver er er r r . . .
#
while True:
    try:
        #
        # Get the temperature reading and format a JSON for our AIO feed.
        #
        print("Posting data...", end='')
        payload = {'value': doGetTemp( ts ) }

        #
        # Post the JSON to AIO using information from the secrets file.
        #
        response = wifi.post(
            "https://io.adafruit.com/api/v2/"+secrets['aio_username']+"/feeds/"+secrets['aio_feed']+"/data",
            json=payload,
            headers={"X-AIO-KEY":secrets['aio_key']})
        #
        # Close out the connection.
        #
        print(response.json())
        response.close()
        print("OK")

    except (ValueError, RuntimeError) as e:
        #
        # In case something happened, reset the Wifi and we'll 
        # try again later.
        #
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue

    response = None
    #
    # modify this value to determine how long the sleep cycle should be.
    # Probably needs to update every hour, but need to look into 
    # sleep cycling of the ESP32 Wifi connection, since THAT is
    # the major power drain.
    #
    time.sleep(3600)
