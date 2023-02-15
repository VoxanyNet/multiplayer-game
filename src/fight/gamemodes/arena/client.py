import pygame
from pygame import Rect

from engine.gamemode_client import GamemodeClient
from fight.gamemodes.arena.player import Player
from fight.gamemodes.arena.floor import Floor
from fight.gamemodes.arena.cursor import Cursor

class Fight(GamemodeClient):
    def __init__(self, fps=60, gravity=9.8, enable_music=False):
        super().__init__(fps=fps)

        self.enable_music = enable_music

        pygame.mouse.set_visible(0)
        
        self.entity_type_map.update(
            {
                "player": Player,
                "floor": Floor
            }
        )

        self.gravity = gravity
    
    def start(self):
        super().start()

        if self.enable_music:
    
            pygame.mixer.music.load("/opt/fightsquares/resources/music.mp3")

            pygame.mixer.music.play(loops=-1)

            pygame.mixer.music.set_volume(0.5)
        
        cursor = Cursor(game=self, updater=self.uuid)

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

        

