import socket
import uuid

import pygame
from pygame import Rect
import pymunk
from pymunk import Body, Shape

from engine.gamemode_client import GamemodeClient
from engine.events import GameStart, LogicTick
from fight.gamemodes.test.entities import TestDynamic
from engine.tile import Tile

class TestClient(GamemodeClient):
    def __init__(self, server_ip: str = socket.gethostname(), server_port: int = 5560, tick_rate=60):
        super().__init__(server_ip=server_ip, server_port=server_port, tick_rate=tick_rate)
        
        self.entity_type_map.update(
            {
                "test_dynamic": TestDynamic
            }
        )

        self.event_subscriptions[LogicTick] += [
            self.spawn_entity,
            self.report_stats
        ]
    
    def report_stats(self, event: LogicTick):

        print(len(self.entities))
    
    def spawn_entity(self, event: LogicTick):
        if pygame.mouse.get_pressed()[0]:
            tile_layout: TileDict = [{
                "height": 20,
                "width": 20,
                "mass": 1,
                "moment": 1,
                "x": 0,
                "y": 0,
                "body_type": "dynamic"
            }]

            entity = TestDynamic(
                origin=pygame.mouse.get_pos(), 
                tile_layout=tile_layout, 
                interaction_rect=Rect(0,0,0,0),
                game=self, 
                updater=self.uuid, 
                id=str(uuid.uuid4())
            )
        
        if pygame.mouse.get_pressed()[2]:
            
            tile_layout: TileDict = [{
                "height": 20,
                "width": 20,
                "mass": 1,
                "moment": 1,
                "x": 0,
                "y": 0,
                "body_type": "static"
            }]

            entity = TestDynamic(
                origin=pygame.mouse.get_pos(), 
                tile_layout=tile_layout, 
                interaction_rect=Rect(0,0,0,0),
                game=self, 
                updater=self.uuid, 
                id=str(uuid.uuid4())
            )


    def start(self, event: GameStart):
        
        body=pymunk.Body(
                mass=1,
                moment=1,
                body_type=pymunk.Body.DYNAMIC
            )
        
        shape=pymunk.Poly(
            body=body,
            vertices=[
                (0,0),
                (0,10),
                (10,10),
                (10,0)
            ]
        )
        
        tile = Tile(
            body=body,
            shape=shape,
            game=self,
            updater=self.uuid,
            id=str(uuid.uuid4()),
            interaction_rect=Rect(0,10,10,10)
        )

        

