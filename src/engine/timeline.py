from typing import Dict
import time

from pygame import Surface

class Timeline:
    def __init__(self, keyframes: Dict[int, Surface], loop: bool = False):
        self.keyframes = keyframes
        
        self.elapsed_time: float = 0
        self.loop = loop

    def get_frame(self, dt: float):
        """Progress the timeline by dt seconds and return frame"""

        self.elapsed_time += dt

        print(self.elapsed_time)

        for end_time, keyframe in self.keyframes.items():

            if self.elapsed_time <= end_time:
                return keyframe
        
        if self.loop:
            # get the last keyframe end time
            last_keyframe_end_time = list(reversed(self.keyframes.keys()))[0] # this is jank

            # get the amount of time that has elapsed since the last frame would have played
            self.elapsed_time = self.elapsed_time - last_keyframe_end_time

            return self.get_frame(dt=0)
        
        return None
    
