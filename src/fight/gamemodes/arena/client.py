import pygame
import pymunk

from engine.gamemode_client import GamemodeClient
from fight.gamemodes.arena.player import Player
from fight.gamemodes.arena.floor import Floor
from fight.gamemodes.arena.cursor import Cursor

class ArenaClient(GamemodeClient):
    def __init__(self, fps=60, enable_music=False):
        super().__init__(fps=fps)

        self.enable_music = enable_music

        pygame.mouse.set_visible(0)
        
        self.entity_type_map.update(
            {
                "player": Player,
                "floor": Floor
            }
        ) 

    def start(self):
        super().start()

        if self.enable_music:
    
            pygame.mixer.music.load("./resources/music.mp3")

            pygame.mixer.music.play(loops=-1)

            pygame.mixer.music.set_volume(0.5)
        
        cursor = Cursor(game=self, updater=self.uuid)

        player = Player(
            pos=(100,100),
            game=self,
            updater=self.uuid,
        )

        self.network_update(
            update_type="create",
            entity_id=player.uuid,
            data=player.dict(),
            entity_type="player"
        )

        


