from Adafruit_BBIO.SPI import SPI
#from PIL import Image
from pprint import pprint
from traceback import print_exception
#import numpy
import time
import logging
import threading
import sys


from startup_sequence import startup_sequence
#from gif_animation import GifAnimation
from sparkle_animation import SparkleAnimation
from lines_animation import LinesAnimation
from rain_animation import RainAnimation
from config import *

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

class Brightbar:
    
    #[brightness, blue, green, red]
    pixel_buffer = [POWER,0,0,0] * LEDS_PER_PANEL * NUM_PANELS
    start_clock = None
    animation_time = 20000
    
    def __init__(self):
        self.init_spi()
        #animation = GifAnimation('gifs/extracted/trippy_39_30x30')
        #animation = SparkleAnimation(None, SparkleAnimation.SPEED_SLOW, [POWER,255,255,255], 1000)
        #animation = SparkleAnimation(None, 2000, [POWER,255,255,255], 1000)
        #animation = LinesAnimation(None, 3000, [POWER,255,255,255], 0)
        animation = RainAnimation(None, .1, [POWER, 0.0, 200.0, 0.0])
        self.animations = [
            SparkleAnimation(None, 2000, [POWER,255,255,255], 1000),
            LinesAnimation(None, 3000, [POWER,255,255,255], 0),
            RainAnimation(None, .1, [POWER, 0.0, 200.0, 0.0])
            ]
        self.render_thread = None
    
    def init_spi(self):
        logging.debug("Initializing spi...")
        self.spi = SPI(0,0)	#/dev/spidev1.0
        
        #   SPI Mode 	Clock Polarity (CPOL/CKP) 	Clock Phase (CPHA) 	Clock Edge (CKE/NCPHA)
        #   0 	        0 	                        0 	                1
        #   1 	        0 	                        1 	                0
        #   2 	        1 	                        0 	                1
        #   3 	        1 	                        1 	                0
        self.spi.mode=0
        self.spi.msh=SPI_CLOCK_RATE #this is clock speed setting 
        self.spi.open(0,0)
        
    def debug_frame(self, data):
        for y in range(PANEL_Y):
            line = str(y) + ": "
            for x in range(PANEL_X):
                offset = (y * PANEL_X + x) * 4
                line += "|" + str(data[offset]) + "," + str(data[offset + 1]) + "," + str(data[offset+2]) + "," + str(data[offset + 3]) 
            print line
        
    #render a full frame
    def render(self):
        #logging.debug("buffer size: " + str(len(self.pixel_buffer)) + " start render: " + str(time.time()))
        start_time = time.time()
        #logging.debug(" start render: " + str(start_time))
        #make a copy of the buffer to work on in case we need to switch the order of bytes
        #data = self.pixel_buffer[:]
        offset = 0
        #the panels run in a snake S shape, so every other line needs to have bytes reversed
        if REVERSE_ALTERNATE_LINES:
            for i in range(0,PANEL_Y):
                if (i % 2) == 0:
                    continue
                offset = i * PANEL_X * 4
                line_length = PANEL_X * 4
                line = data[offset:offset + line_length]
                reversed_line = [0] * line_length
                j = line_length - 4 #start one color from the end, and go backwards through the line
                while j >= 0:
                    reversed_line[line_length - j - 4] = line[j]
                    reversed_line[line_length - j - 3] = line[j + 1]
                    reversed_line[line_length - j - 2] = line[j + 2]
                    reversed_line[line_length - j - 1] = line[j + 3]
                    j = j - 4
                    
                data[offset:offset + PANEL_X * 4] = reversed_line
            
        #self.write_apa102(data)
        #logging.debug("length of buffer: " + str(len(self.pixel_buffer)))
        #logging.debug(self.pixel_buffer)
        self.write_apa102(self.pixel_buffer)
        end_time = time.time();
        #logging.debug("end render: " + str(end_time) + " elapsed: " + str(end_time - start_time))
        #import pdb
        #pdb.set_trace()
        
        
    def write_apa102(self, data):
        #start frame, 32 bits of zero
        self.spi.writebytes([0] * 4)
        
        #write RGB data
        #chunk the data out in 1024 byte blocks
        for i in range(0,len(data),1024):
            length = len(data)
            if((i + 1024) > length):
                #end = length - (i+1024 - length)
                chunk = data[i:]
            else:
                #end = i + 1024
                chunk = data[i:i+1024]
            self.spi.writebytes(chunk)
        
        #write footer. This is total numnber of LEDS / 2 bits of 1's
        num_dwords = LEDS_PER_PANEL * NUM_PANELS / 32 
        for i in range(num_dwords):
            self.spi.writebytes([0xff, 0x00, 0x00, 0x00]) #the datasheet calls for 1's here, but internet says 0s work better? the fast LED lib does both?
        
        
    def clear(self):
        self.pixel_buffer = [POWER,0,0,0] * LEDS_PER_PANEL * NUM_PANELS 
                
    
    def calculate_fps(self):
        now = time.time()
        delta = now - self.start_clock
        frame_time = delta/self.frame_count
        self.fps = 1/frame_time
        logging.debug("elapsed seconds: " + str(delta) + " frame count: " + str(self.frame_count) + " current fps: " + str(self.fps))
        
        
    def animate(self):
        
        if self.start_clock == None:
            self.frame_count = 0
            self.start_clock = time.time()
            
        elapsed_time = time.time() - self.start_clock
        num_animations = int(round(elapsed_time / (self.animation_time / 1000)))
        current_animation = int(num_animations) % len(self.animations)
        #logging.debug("elapsed time: " + str(elapsed_time) + " num animations:" + str(num_animations) + " current animation:" + str(current_animation))
        
        animation = self.animations[current_animation]
        
        frame = animation.get_next_frame()
        
        if frame == None:
            time.sleep(.001)
            return
        
        self.frame_count = self.frame_count + 1
        
        if self.frame_count % 100 == 0:
            self.calculate_fps()
            
        line_length = animation.width * 4
        
        for y in range(animation.height):
            frame_offset = y * line_length
            line = frame[frame_offset:frame_offset + line_length]
            buffer_offset =  ( ( (int(animation.destination_y_offset) + y) * PANEL_X ) + int(animation.destination_x_offset) )  * 4
            self.pixel_buffer[buffer_offset:buffer_offset + line_length] = line
                
    def render_loop(self):
        try:
            while 1:
                brightbar.animate()
                brightbar.render()
        except:
            print_exception(*sys.exc_info())
            
    def start(self):
        if STARTUP_SEQUENCE:
            startup_sequence(self);
        if self.render_thread == None:
            self.render_thread = threading.Thread(name="RenderThread", target=self.render_loop)
        self.render_thread.start()
    
    def stop(self):
        self.render_thread.stop()
            
        
logging.debug("Starting program...")
brightbar = Brightbar()
logging.debug("rendering...")
brightbar.start()
    
