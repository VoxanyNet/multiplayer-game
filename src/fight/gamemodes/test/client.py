import socket
import uuid

import pygame
from pygame import Rect
import pymunk
from pymunk import Body, Shape

from engine.gamemode_client import GamemodeClient
from engine.events import GameStart, LogicTick
from engine.tile import Tile

class TestClient(GamemodeClient):
    def __init__(self, server_ip: str = socket.gethostname(), server_port: int = 5560, tick_rate=60):
        super().__init__(server_ip=server_ip, server_port=server_port, tick_rate=tick_rate)

        self.event_subscriptions[LogicTick] += [
            self.spawn_entity,
            self.report_stats
        ]
    
    def report_stats(self, event: LogicTick):

        print(len(self.entities))
    
    def spawn_entity(self, event: LogicTick):
        
        if pygame.mouse.get_pressed()[0]:
            body=pymunk.Body(
                mass=20,
                moment=10,
                body_type=pymunk.Body.DYNAMIC
            )

            body.position = pygame.mouse.get_pos()
        
            shape=pymunk.Poly.create_box(
                body=body,
                size=(20,20)
            )
            
            tile = Tile(
                body=body,
                shape=shape,
                game=self,
                updater=self.uuid,
                id=str(uuid.uuid4()),
                interaction_rect=Rect(0,10,10,10)
            )

        if pygame.mouse.get_pressed()[2]:
            
            body=pymunk.Body(
                mass=20,
                moment=1,
                body_type=pymunk.Body.STATIC
            )

            body.position = pygame.mouse.get_pos()
        
            shape=pymunk.Poly(
                body=body,
                vertices=[
                    (0,0),
                    (0,20),
                    (20,20),
                    (20,0)
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


    def start(self, event: GameStart):
        pass

        

