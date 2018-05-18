import time
from config import *

def startup_sequence(brightbar):
    #import pdb
    #pdb.set_trace()
    print("Running calibration test...")
    delay = 50 / 1000
    
    def horizontal_line(row, color):
        for i in range(PANEL_X):
            offset = (row * PANEL_X + i) * 4
            brightbar.pixel_buffer[offset] = color[0]
            brightbar.pixel_buffer[offset + 1] = color[1]
            brightbar.pixel_buffer[offset + 2] = color[2]
            brightbar.pixel_buffer[offset + 3] = color[3]
    
    def vertical_line(column, color):
        for i in range(PANEL_Y):
            offset = (i * PANEL_X + column) * 4
            brightbar.pixel_buffer[offset] = color[0]
            brightbar.pixel_buffer[offset + 1] = color[1]
            brightbar.pixel_buffer[offset + 2] = color[2]
            brightbar.pixel_buffer[offset + 3] = color[3]
            
    def all_pixels(colors):
        for i in range(PANEL_Y):
            for j in range(0,PANEL_X,len(colors)/4):
                offset = (i * PANEL_X + j) * 4
                brightbar.pixel_buffer[offset:offset+len(colors)] = colors
    
    #thanks to adafruit example!
    def wheel(position):
        position = 255 - position
        if position < 85:
            primary = position * 3
            secondary = 255 - position * 3
            return [POWER, secondary, 0, primary]
        elif position < 170:
            position -= 85
            primary = position * 3
            secondary = 255 - position * 3
            return [POWER, 0, primary, secondary]
        else:
            position -= 170
            primary = position * 3
            secondary = 255 - position * 3
            return [POWER, primary, secondary, 0]
        
    
    #horizontal lines        
    print("horizontal lines...")
    for color in [[255,0,0], [0,255,0],[0,0,255]]:
        for brightness in [DIM, MEDIUM, BRIGHT]:
            for i in range(PANEL_Y):
                time.sleep(delay)
                brightbar.clear()
                horizontal_line(i, [brightness] + color )
                brightbar.render()
                
    #vertical lines        
    print("vertical lines...")
    for color in [[255,0,0], [0,255,0],[0,0,255]]:
        for brightness in [DIM, MEDIUM, BRIGHT]:
            for i in range(PANEL_X):
                time.sleep(delay)
                brightbar.clear()
                vertical_line(i, [brightness] + color )
                brightbar.render()
                
    #buffer flood
    brightbar.clear()
    #blue
    for i in range(0,LEDS_PER_PANEL * 4, 4):
        brightbar.pixel_buffer[i:i+4] = [POWER, 255, 0, 0]
    brightbar.render()
    time.sleep(2)
    #green
    for i in range(0,LEDS_PER_PANEL * 4, 4):
        brightbar.pixel_buffer[i:i+4] = [POWER, 0, 255, 0]
    brightbar.render()
    time.sleep(2)
    #red
    for i in range(0,LEDS_PER_PANEL * 4, 4):
        brightbar.pixel_buffer[i:i+4] = [POWER, 0, 0, 255]
    brightbar.render()
    time.sleep(2)
        
                
    #all pixels, color chase
    red = [POWER, 255, 0, 0]
    green = [POWER, 0, 255, 0]
    blue = [POWER, 0, 0, 255]
    for i in range(10):
        time.sleep(.3)
        all_pixels(red + green + blue)
        brightbar.render()
        time.sleep(.3)
        all_pixels(blue + red + green)
        brightbar.render()
        time.sleep(.3)
        all_pixels(green + blue + red)
        brightbar.render()
        
    #color wheel
    for j in range(10):
        for position in range(256):
            color = wheel(position)
            #print color
            for i in range(0, LEDS_PER_PANEL * 4, 4):
                brightbar.pixel_buffer[i:i+4] = color
            brightbar.render()
            time.sleep(DELAY)
        