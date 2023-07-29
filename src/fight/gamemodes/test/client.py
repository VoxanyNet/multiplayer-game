import socket
import uuid

import pygame
from pygame import Rect

from engine.gamemode_client import GamemodeClient
from engine.events import GameStart
from fight.gamemodes.test.entities import TestDynamic
from engine.tileentity import TileEntity, TileDict

class TestClient(GamemodeClient):
    def __init__(self, server_ip: str = socket.gethostname(), server_port: int = 5560, tick_rate=60):
        super().__init__(server_ip=server_ip, server_port=server_port, tick_rate=tick_rate)
        
        self.entity_type_map.update(
            {
                "test_dynamic": TestDynamic
            }
        )
    
    def start(self, event: GameStart):
        tile_layout: TileDict = [{
            "height": 20,
            "width": 20,
            "mass": 1,
            "moment": 1,
            "x": 0,
            "y": 0
        }]

        example_entity = TestDynamic(
            origin=[500,500], 
            tile_layout=tile_layout, 
            interaction_rect=Rect(0,0,0,0),
            game=self, 
            updater=self.uuid, 
            id=str(uuid.uuid4())
        )

        

