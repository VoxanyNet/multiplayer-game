import pygame
from pygame import Rect

from engine import Game
from player import Player
from weapon import Weapon
from sword import Sword
from floor import Floor
from cursor import Cursor


class Fight(Game):
    def __init__(self, fps=60, gravity=9.8, enable_music=False):
        super().__init__(fps=fps)

        self.enable_music = enable_music
        
        self.entity_type_map.update(
            {
                "player": Player,
                "weapon": Weapon,
                "sword": Sword,
                "floor": Floor,
                "cursor": Cursor
            }
        )

        self.gravity = gravity
    
    def start(self, server_ip, server_port=5560):
        super().start(server_ip=server_ip,server_port=server_port)

        if self.enable_music:
    
            pygame.mixer.music.load("/opt/fightsquares/resources/music.mp3")

            pygame.mixer.music.play(loops=-1)

            pygame.mixer.music.set_volume(0.5)

        player = Player(
            rect=Rect(100,100,50,50),
            game=self,
            updater=self.uuid,
        )

        self.network_update(
            update_type="create",
            entity_id=player.uuid,
            data=player.dict(),
            entity_type="player"
        )

        


