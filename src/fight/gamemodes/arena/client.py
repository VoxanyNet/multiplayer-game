import pygame
from pygame import Rect

from engine.gamemode_client import GamemodeClient
from engine.events import GameStart
from fight.gamemodes.arena.entities import Player, Floor, Cursor, Shotgun

class ArenaClient(GamemodeClient):
    def __init__(self, tick_rate=60, gravity=9.8, enable_music=False):
        super().__init__(tick_rate=tick_rate)

        self.enable_music = enable_music

        pygame.mouse.set_visible(0)
        
        self.entity_type_map.update(
            {
                "player": Player,
                "floor": Floor,
                "shotgun": Shotgun,
                "cursor": Cursor
            }
        )

        self.gravity = gravity
    
    def start(self, event: GameStart):
        
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

        print(self.entities)

        

