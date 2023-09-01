from typing import Dict
import time

from pygame import Surface

class Timeline:
    def __init__(self, keyframes: Dict[int, Surface], loop: bool = False):
        self.keyframes = keyframes
        
        self.start_time: float = None
        self.loop = loop

    def play(self):

        self.start_time = time.time()
    
    @property
    def current_frame(self):

        if not self.start_time:
            elapsed_time = 0
        
        else:
            elapsed_time = time.time() - self.start_time
        
        for end_time, keyframe in self.keyframes.items():
            

            if elapsed_time <= end_time:
                return keyframe
        
        if self.loop:
            # reset the start time to exactly when the last frame was scheduled to end

            # get the last keyframe end time
            last_keyframe_end_time = list(reversed(self.keyframes.keys()))[0] # this is jank

            self.start_time += last_keyframe_end_time
            
            return self.current_frame

        # if the timeline doesnt loop, and there are no valid keyframes
        return None
    
