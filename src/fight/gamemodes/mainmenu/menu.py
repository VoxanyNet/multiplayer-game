import pygame
from pygame import Rect

from engine.gamemode_client import GamemodeClient
from fight.gamemodes.mainmenu.play_button import PlayButton
from fight.gamemodes.mainmenu.title import Title

class Menu(GamemodeClient):
    def __init__(self, fps=60, enable_music=False):
        super().__init__(fps=fps)

        self.enable_music = enable_music

        #pygame.mouse.set_visible(0)
        
        self.entity_type_map.update(
            {
                "play_button": PlayButton,
                "title": Title
            }
        )
    
    def start(self, server_ip, server_port=5560):
        super().start(server_ip=server_ip,server_port=server_port)

        if self.enable_music:
    
            pygame.mixer.music.load("/opt/fightsquares/resources/music.mp3")

            pygame.mixer.music.play(loops=-1)

            pygame.mixer.music.set_volume(0.5)

        play_button = PlayButton()

        


