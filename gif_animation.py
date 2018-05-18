from PIL import Image
from animation import Animation
import time
import logging
from config import *

class GifAnimation(Animation):
    
    def __init__(self, folder):
        Animation.__init__(self)
        self.load(folder)
    
    def load(self, folder):
        from os import listdir
        from os.path import isfile, join
        
        print "loading animation: " + folder
        
        def sort_by_name(file1, file2):
            file1 = file1.replace('.png','')
            file1 = file1.replace('frame_','')
            file2 = file2.replace('.png','')
            file2 = file2.replace('frame_','')
            frame_1 = int(file1)
            frame_2 = int(file2)
            return frame_1 - frame_2
            
        files = [f for f in listdir(folder) if isfile(join(folder, f)) and f.startswith('frame')]
        files.sort(sort_by_name)
        
        first = True
        
        for file in files:
            img = Image.open(folder + '/' + file)
            if first:
                first = False
                self.width, self.height = img.size
            rgb = img.convert('RGB')
            self.add_frame(rgb.load())
            
        print "loaded " + str(len(self.frames)) + " frames w: " + str(self.width) + " h: " + str(self.height)
            
        path = folder.split("/")
        folder_name = path[len(path)-1]
        gif = Image.open(folder + "/" + folder_name + '.gif')
        self.frame_delay = int(gif.info['duration'])
        logging.debug("frame delay:" + str(self.frame_delay))
        
        #clamp at 20ms delay, some gifs improperly store the entire animation duration in the 'duration' property, it's supposed to be the frame duration
        if self.frame_delay > 20:
            self.frame_delay = 20
            
    def add_frame(self, frame):
        """ append frame to the list of frames. convert to BGR colorspace and add power byte so that data is in correct format for rendering"""
        #import pdb
        
        frame_buffer = [0] * self.height * self.width * 4
        for y in range(self.height):
            for x in range(self.width):
                #pdb.set_trace()
                pixel = frame[x,y]
                pixel = self.adjust_brightness(pixel)
                pixel = list(pixel)
                pixel.reverse()
                color = [POWER] + pixel
                offset = ( (y * self.width) + x) * 4
                #logging.debug("offset: " + str(offset))
                frame_buffer[offset:offset+4] = color
        self.frames.append(frame_buffer)
        
    def get_next_frame(self):
        now = time.time()
        if self.last_frame_time == None:
            self.last_frame_time = now
        delta = now - self.last_frame_time
        self.calculate_position()
        
        delay = int(self.frame_delay) / 1000.0
        
        #logging.debug("now: " + str(now) + "last frame:" + str(self.last_frame_time) + " delta:" + str(delta) + " delay:" + str(delay) + " frame_delay:" + str(self.frame_delay))
        
        if delta < delay:
            #logging.debug("waiting to render...")
            return None
            
        self.last_frame_time = now
            
        self.frame_count += 1
        self.current_frame += 1
        
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
            
        return self.frames[self.current_frame]