from random import random
from animation import Animation
from pprint import pprint
import time
import logging
import math
from config import *

class SparkleAnimation(Animation):
    MAX_SPARKLES = LEDS_PER_PANEL * NUM_PANELS / 2
    SPEED_FAST = 100
    SPEED_MEDIUM = 400
    SPEED_SLOW = 700
    
    class Sparkle:
        def __init__(self, lifetime, ramp, color, x, y):
            
            if not lifetime:
                lifetime = 500
                
            self.is_dead = False
            self.start_lifetime = None
                
            #this is the rate at which the sparkles will display overall. This is the maximum time in ms that the sparkle will live for,
            #meaning the total fade in and fade out time
            self.lifetime = lifetime / 1000
            self.current_lifetime = 0
            
            #this is the maximum allowed ramp up and down time for the fading in and out, in ms. Must be less than half of the lifetime.
            if not ramp:
                ramp = self.lifetime / 2
            self.ramp = ramp
                
            self.current_color = [POWER, 0, 0, 0]
            
            if not x:
                x = random() * PANEL_X
            self.x = int(x)
            
            if not y:
                y = random() * PANEL_Y
            self.y = int(y)
            
            if not color:
                color = [POWER, 255,255,255]
            self.color = color
                
            
        def tick(self, adjust_brightness):
            now = time.clock()
            if not self.start_lifetime:
                self.start_lifetime = now
            
            self.current_lifetime = now - self.start_lifetime
            
            if self.current_lifetime > self.lifetime:
                self.die()
                return
            
            
            #determine if we're ramping up
            if self.current_lifetime <= self.ramp:
                fade_multiplier = self.current_lifetime / self.ramp
            #or if we're ramping down
            elif self.lifetime - self.current_lifetime < self.ramp:
                ramp_down = self.lifetime - self.current_lifetime
                fade_multiplier = ramp_down / self.ramp
                #logging.debug("ramp: " + str(self.ramp) + " ramp_down:" + str(ramp_down) + " multiplier: " + str(fade_multiplier))
            #or just displaying at full color
            else:
                fade_multiplier = 1
                
            r = int(round(self.color[1] * fade_multiplier))
            g = int(round(self.color[2] * fade_multiplier))
            b = int(round(self.color[3] * fade_multiplier))
            (r,g,b) = adjust_brightness((r,g,b));
                
            self.current_color = [POWER, b, g, r] 
            
        def render(self, buffer):
            offset = ((PANEL_X * self.y) + self.x) * 4
            buffer[offset:offset+4] = self.current_color
                
        def die(self):
            self.is_dead = True
            
    
    def __init__(self, spawn_rate, speed, color, color_wheel_speed):
        Animation.__init__(self)
        if not spawn_rate:
            spawn_rate = 1/self.MAX_SPARKLES
        self.spawn_rate = spawn_rate
        self.speed = speed
        self.color = color
        self.color_wheel_speed = color_wheel_speed
        self.last_spawn_time = None
        self.start_time = None
        self.width = PANEL_X
        self.height = PANEL_Y
        self.sparkles = []
    
    def load(self, folder):
        pass
    
    def clear(self):
        self.buffer = [POWER,0,0,0] * PANEL_X * PANEL_Y
            
    
    def wheel(self,position):
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
            
        if self.color_wheel_speed > 0:
            converted_time =  (now - self.start_time) * 1000 
            time_modulus = converted_time % self.color_wheel_speed
            scaled_time = int(time_modulus * 255 / 1000)
            #logging.debug("scaled time: " + str(scaled_time))
            self.current_color = self.wheel(scaled_time)
        else:
            self.current_color = self.color
            
        if (now - self.last_spawn_time) > self.spawn_rate:
            if len(self.sparkles) < self.MAX_SPARKLES:
                #logging.debug("current color: " + str(self.current_color))
                lifetime = random() * self.speed
                if lifetime < 500:
                    lifetime = 500.0
                sparkle = self.Sparkle(lifetime, None, self.current_color, None, None)
                #sparkle = self.Sparkle(random() * 500, None, [POWER,255,255,255], None, None)
                for s in self.sparkles:
                    if (sparkle.x == s.x) and (sparkle.y ==s.y):
                        sparkle.x = sparkle.x + 1
                #[POWER, int(random()*255),int(random()*255),int(random() * 255)], None, None)
                self.sparkles.append(sparkle)
                self.last_spawn_time = now
            
        #cull any dead sparkles
        self.sparkles = [sparkle for sparkle in self.sparkles if not sparkle.is_dead]
            
        for sparkle in self.sparkles:
            sparkle.tick(self.adjust_brightness)
            sparkle.render(self.buffer)
                
        
        #logging.debug("now: " + str(now) + "last frame:" + str(self.last_frame_time) + " delta:" + str(delta) + " delay:" + str(delay) + " frame_delay:" + str(self.frame_delay))
        
        if delta < delay:
            return None
            
        self.last_frame_time = now
            
        return self.buffer