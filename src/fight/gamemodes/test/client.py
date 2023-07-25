import socket
import uuid

import pygame
from pygame import Rect

from engine.gamemode_client import GamemodeClient
from engine.events import GameStart
from fight.gamemodes.test.entities import TestDynamic
from engine.tileentity import TileEntity

class TestClient(GamemodeClient):
    def __init__(self, server_ip: str = socket.gethostname(), server_port: int = 5560, tick_rate=60):
        super().__init__(server_ip=server_ip, server_port=server_port, tick_rate=tick_rate)
        
        self.entity_type_map.update(
            {
                "test_dynamic": TestDynamic
            }
        )
    
    def start(self, event: GameStart):

        example_entity = TestDynamic(interaction_rect=Rect(0,0,0,0), game=self, updater=self.uuid, id=str(uuid.uuid4()))

        

