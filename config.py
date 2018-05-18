NUM_PANELS = 1 #the number of panels we're driving
PANEL_X = 19 #number of leds per panel in the X direction
PANEL_Y = 8 #number of leds per panel in the Y direction
LEDS_PER_PANEL = PANEL_X * PANEL_Y
FPS = 30
DELAY = 1000/FPS/1000
DIM = 128 + 64 + 32 + 1
MEDIUM = 128 + 64 + 32 + 9 
BRIGHT = 128 + 64 + 32 + 31 
POWER = BRIGHT
SPI_CLOCK_RATE = 2000000

#this is used to indicate that every alternate line should have the data reversed. This is handy for example, in large panels that 
#are laid out in a strip of lights that zig-zags and isn't a true X/Y grid.
REVERSE_ALTERNATE_LINES = False

#should an initial calibration/startup sequence run when booting the device
STARTUP_SEQUENCE = False

#this is the amount of time it takes to shift out the data to the LED array
FRAME_DELAY_DELTA = 1/SPI_CLOCK_RATE * NUM_PANELS * LEDS_PER_PANEL * 4

#additional delay that can be changed to tweak rendering speed depending on processor speed
ADDITIONAL_DELAY_DELTA = .00
