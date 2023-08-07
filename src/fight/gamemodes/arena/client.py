import socket
import uuid

import pygame
from pygame import Rect

from engine.gamemode_client import GamemodeClient
from engine.events import GameStart
from fight.gamemodes.arena.entities import Player, Floor, Shotgun, Portal, Wall

class ArenaClient(GamemodeClient):
    def __init__(self, server_ip: str = socket.gethostname(), server_port: int = 5560, gravity=9.8, enable_music=False):
        super().__init__(server_ip=server_ip, server_port=server_port)

        self.enable_music = enable_music

        #pygame.mouse.set_visible(0)
        
        self.entity_type_map.update(
            {
                "player": Player,
                "floor": Floor,
                "shotgun": Shotgun,
                "portal": Portal,
                "wall": Wall
            }
        )

        self.gravity = gravity
    
    def start(self, event: GameStart):

        player = Player(
            interaction_rect=Rect(100,100,50,50),
            game=self,
            updater=self.uuid,
            gravity=2,
            id=str(uuid.uuid4())
        )

        shotgun = Shotgun(
            owner=player, 
            interaction_rect=Rect(0,0,39,11),
            game=self,
            updater=self.uuid,
            id=str(uuid.uuid4())
        )

        player.weapon = shotgun

        

