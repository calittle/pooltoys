# PoolToys
This is an experimental project. My wife constantly wants to know the pool temperature because she is fickle. She only likes to swim at certain water temperatures -- usually when the water is akin to a bath. We had, for a moment, a cheap (well, not really) wireless thermometer that transmitted the temperature to a convenient display in the house. But, it lasted only a year. I didn't want to keep replacing it, so I decided to build this thing.

# What is it?
A small Arduino-based microcontroller that periodically reads the temperature from a sensor and uploads the data to a website. Ultimately that was the singular goal, but things being as they are and people being themselves, the goals have expanded to include an Alexa skill so we can ask our Amazon assistant to report the pool temperature. This has the added bonus of also including a time difference analysis -- if the temperature readings are long in the tooth, Alexa will says so, which means something might not be working correctly.

# How To
Until I have time to properly document this, review the schematic, source code (code.py) and this simple list:
1. Build the circuit. 
![schematic](https://raw.githubusercontent.com/calittle/pooltoys/master/circuit/schematic.png)
1. Create your io.adafruit.com account.
1. Modify code.py with your adafruit account key.
1. Modify secret.py with your wifi connection information
1. Upload code.py and secret.py to your Metro board.

If you've gotten this far, good. Now obtain a waterproof project box that will fit your stuff. Don't forget to take into account plugs into the Metro board. Get some PG-7 glands too!
1. Drill holes in the project box to fit your gland. I think it's about 11.5MM or so. [See here](http://radel.co.za/website/index.php?option=com_content&view=article&id=90:pg-gland-thread-sizes&catid=38:bopla&Itemid=56)
1. Fit glands. I didn't tap the holes. Insert > O-Ring > Box/Hole > Nut
1. Temporarily disconnect DS12B20 from the board. 
1. Insert DS12B20 cables into gland closure nut, then feed through the gland and box, wire back up to board.
1. Leave a little slack inside the box for the DS12B20 wire, then tighten the closure nut.
1. Repeat the gland-drill-cable for your Metro power supply. I hope you got the right kind of waterproof power supply situation worked out.
1. Seal the box.

Take this puppy outside, dunk the sensor in your skimmer box or over the side of the pool, or where ever might be good. Wear rubber shoes and connect the power to the box and hopefully your 
NuPixel goes blue and you're transmitting data.

# To Do
1. Wire up a PV cell to a charging circuit for resuppling precious volts to a LiPo battery for powering the Metro.
1. Get the Alexa skill working with authorization to Adafruit so you can individually personalize the skill to your settings rather than mine ;-)
