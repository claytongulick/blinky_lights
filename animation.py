import time
import logging
from config import *

class Animation:
    """Base class for animations"""
    
    #lookup table for a brightness curve to drive modified perceived brightness with PWM
    GAMMA =   [    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
                    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
                    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
                    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
                    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
                   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
                   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
                   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
                   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
                   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
                   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
                   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
                  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
                  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
                  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
                  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255   ]
                      
    def __init__(self):
        self.start_clock = time.time()
        self.last_frame_time = None #self.start_clock
        self.frames = []
        self.current_frame = -1
        self.frame_delay = 0
        self.frame_count = 0
        self.fps = 0
        self.destination_y_offset = 0
        self.direction_y = 1
        self.destination_x_offset = 0
        self.direction_x = 1
        self.velocity_y = 0 #pixels per second
        self.velocity_x = 0
    
    def load(self):
        pass
    
    def adjust_brightness(self, pixel):
        """ adjust the brightness of the pixel to account for pwm brightness perception nonlinearity"""
        r,g,b = pixel
        r = self.GAMMA[r]
        if r < 3: r = 0
        g = self.GAMMA[g]
        if g < 3: g = 0
        b = self.GAMMA[b]
        if b < 3: b = 0
        return (r,g,b)
        
    def calculate_position(self):
        #calculate the destination offset based on the velocity of the animation in the x and y direction
        delta = time.time() - self.last_frame_time
        if int(self.destination_y_offset) + self.height >= PANEL_Y:
            self.direction_y = -1
            self.destination_y_offset = PANEL_Y - self.height
                
        if int(self.destination_y_offset) < 0:
            self.direction_y = 1
            self.destination_y_offset = 0
            
        if int(self.destination_x_offset) + self.width >= PANEL_X:
            self.direction_x = -1
            self.destination_x_offset = PANEL_X - self.width
                
        if int(self.destination_x_offset) <= 0:
            self.direction_x = 1
            self.destination_x_offset = 0
                
        self.destination_y_offset += self.velocity_y * delta * self.direction_y
        self.destination_x_offset += self.velocity_x * delta * self.direction_x
        #logging.debug("y: " + str(self.destination_y_offset) + " x: " + str(self.destination_x_offset))
        
    
    def get_next_frame(self):
        self.frame_count += 1
        self.current_frame += 1
        
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
            
        #print "returning frame: " + str(self.current_frame) + " of " + str(len(self.frames))
        
        return self.frames[self.current_frame]