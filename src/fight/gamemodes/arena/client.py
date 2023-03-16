import pygame
from pygame import Rect

from engine.gamemode_client import GamemodeClient
from fight.gamemodes.arena.entities import Player, Floor, Cursor, Shotgun

class ArenaClient(GamemodeClient):
    def __init__(self, server_address, fps=60, enable_music=False):
        super().__init__(server_address, fps=fps)

        self.enable_music = enable_music

        pygame.mouse.set_visible(0)
        
        self.entity_type_map.update(
            {
                "player": Player,
                "floor": Floor,
                "shotgun": Shotgun
            }
        )
    
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

        shotgun = Shotgun(
            owner=player, 
            rect=Rect(0,0,39,11),
            game=self,
            updater=self.uuid
        )

        player.weapon = shotgun

        self.network_update(
            update_type="create",
            entity_id=player.uuid,
            data=player.dict(),
            entity_type="player"
        )

        self.network_update(
            update_type="create",
            entity_id=shotgun.uuid,
            data=shotgun.dict(),
            entity_type="shotgun"
        )

        if self.is_master:
            floor = Floor(
                rect=Rect(0,600,1920,20),
                game=self,
                updater="server"
            )

            self.network_update(
                update_type="create",
                entity_id=floor.uuid,
                data=floor.dict(),
                entity_type="floor"
            )

        print(self.entities)

        

