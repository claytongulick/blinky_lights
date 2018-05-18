from random import random
from animation import Animation
from pprint import pprint
import time
import logging
import math
import sys
from config import *
from traceback import print_exception

class RainAnimation(Animation):
    MAX_LINES = 25 
    
    class Line:
        def __init__(self, fade_speed, color, x, y, velocity):
            
            self.buffer = [POWER, 0.0, 0.0, 0.0] * PANEL_Y
                
            self.is_dead = False
            
            if not x:
                x = random() * (PANEL_X - 1)
            self.x = int(x)
            
            if not y:
                y = random() * (PANEL_Y - 1)
            self.current_y = y
            self.y = int(round(y))
            
            self.buffer[self.y * 4:(self.y * 4) + 4] = [POWER, 255.0,255.0,255.0]
            
            if not velocity:
                velocity = .200
            if velocity < .1:
                velocity = .1
            self.velocity = velocity
            
            if not color:
                color = [POWER, 0.0,255.0,0.0]
            self.color = color
            #normalize based on a % of 255
            self.fade_rate = [color[1]/255.0, color[2]/255.0, color[3]/255.0]
            #change the fade rate based on normalized color component
            self.fade_rate = [self.fade_rate[0] * fade_speed, 
                              self.fade_rate[1] * fade_speed, 
                              self.fade_rate[2] * fade_speed]
            self.render_count = 0
            #logging.debug(self.fade_rate)
            
                
        def fade(self):
            for i in range(PANEL_Y):
                offset = i * 4
                
                if i == self.y:
                    #logging.debug("skipping: " + str(i))
                    #logging.debug( self.buffer[offset:offset+4] )
                    continue
                
                self.buffer[offset:offset+4] = [
                        self.buffer[offset], #power
                        self.buffer[offset + 1] * (1-self.fade_rate[0]),
                        self.buffer[offset + 2] * (1-self.fade_rate[1]),
                        self.buffer[offset + 3] * (1-self.fade_rate[2])
                    ]
            #logging.debug("fade")
            #logging.debug(self.buffer)
            
        def tick(self, adjust_brightness):
            now = time.clock()
            
            self.fade()
            self.die()
            
            if self.current_y > PANEL_Y + 1:
                return
            
            last_y = int(round(self.current_y))
            
            #move
            self.current_y = self.current_y + self.velocity #this is the floating point location
            self.y = int(round(self.current_y)) #this is the integer, rounded location
            
            #if we've moved down a pixel
            if self.y > last_y:
                #set the previous location to the current color
                offset = last_y  * 4
                self.buffer[offset:offset+4] = self.color
                #logging.debug("self.y:" + str(self.y) + " last_y: " + str(last_y))
                
                #white leading pixel    
                if self.y <= PANEL_Y:
                    offset = self.y * 4
                    self.buffer[offset:offset+4] = [POWER, 255.0,255.0,255.0]
            #logging.debug("current_y:" + str(self.current_y) + " y:" + str(self.y) + " last_y:" + str(last_y))        
            #logging.debug(self.buffer)
                        
            
        def render(self, buffer):
            #self.render_count = self.render_count + 1
            #if self.render_count > 5:
            #    sys.exit(0)
            #logging.debug(self.buffer)
            for i in range(PANEL_Y):
                offset = ((PANEL_X * i) + self.x) * 4
                self_offset = i * 4
                for j in range(4):
                    #logging.debug(str(offset+j))
                    try:
                        buffer[offset+j] = int(round(self.buffer[self_offset+j]))
                    except:
                        print_exception(*sys.exc_info())
                        logging.debug("self.x:" + str(self.x) + "i:" + str(i) + "offset:" + str(offset) + " self offset:"+str(self_offset))
                        
                    
                
        def die(self):
            """check to see if all of the pixels in the buffer have faded to 0, 
            if so, we're dead"""
            self.is_dead = True
            for i in range(PANEL_Y):
                offset = i * 4
                if self.buffer[offset+1] > 1 or \
                    self.buffer[offset+2] > 1 or \
                    self.buffer[offset+3] > 1:
                         self.is_dead = False
                         return
            #logging.debug("line dead")
            
    
    def __init__(self, spawn_rate, fade_speed, color):
        Animation.__init__(self)
        if not spawn_rate:
            spawn_rate = 1/self.MAX_LINES
        self.spawn_rate = spawn_rate
        self.fade_speed = fade_speed
        self.color = color
        self.last_spawn_time = None
        self.start_time = None
        self.width = PANEL_X
        self.height = PANEL_Y
        self.lines = []
    
    def load(self, folder):
        pass
    
    def clear(self):
        self.buffer = [POWER,0,0,0] * PANEL_X * PANEL_Y
        
        
    def get_next_frame(self):
        self.clear()
        now = time.clock()
        if not self.start_time:
            self.start_time = now
        if not self.last_frame_time:
            self.last_frame_time = now
            
        delta = now - self.last_frame_time
        
        delay = int(self.frame_delay) / 1000.0
        
        if not self.last_spawn_time:
            self.last_spawn_time = now
            
        if (now - self.last_spawn_time) > self.spawn_rate:
            #logging.debug("current color: " + str(self.current_color))
            if len(self.lines) < self.MAX_LINES:
                
                line = self.Line(self.fade_speed, 
                                self.color, 
                                round(random() * (PANEL_X - 1)), 
                                round(random() * PANEL_Y / 3), # don't want trails starting right at the bottom
                                random()/10) # velocity
                self.last_spawn_time = now
            
                #[POWER, int(random()*255),int(random()*255),int(random() * 255)], None, None)
                self.lines.append(line)
            
        #cull any dead lines
        self.lines = [line for line in self.lines if not line.is_dead]
            
        for line in self.lines:
            line.tick(self.adjust_brightness)
            line.render(self.buffer)
        
        #logging.debug("now: " + str(now) + "last frame:" + str(self.last_frame_time) + " delta:" + str(delta) + " delay:" + str(delay) + " frame_delay:" + str(self.frame_delay))
        
        if delta < delay:
            return None
            
        self.last_frame_time = now
            
        return self.buffer