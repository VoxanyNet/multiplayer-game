import socket
import uuid
import time

import pygame
from pygame import Rect
import pymunk
from pymunk import Body, Shape

from engine.gamemode_client import GamemodeClient
from engine.events import GameStart, Tick
from engine.tile import Tile
from fight.gamemodes.ragdoll.entities import ConnectableTile, ConnectableTileMaker

class RagdollClient(GamemodeClient):
    def __init__(self, server_ip: str = socket.gethostname(), server_port: int = 5560, network_compression: bool = True):
        super().__init__(server_ip=server_ip, server_port=server_port, network_compression=network_compression)

        self.event_subscriptions[Tick] += [
            self.spawn_entity
        ]

        self.entity_type_map.update(
            {
                "connectable_tile": ConnectableTile,
                "connectable_tile_maker": ConnectableTileMaker
            }
        )

        #collision_handler = self.space.add_collision_handler(1, 1)

        #collision_handler.begin = collision_callback


        self.last_spawn = 0
    
    def spawn_entity(self, event: Tick):
        
        if time.time() - self.last_spawn < 0.2:
            return
        
        if pygame.key.get_pressed()[pygame.K_e]:
            body=pymunk.Body(
                mass=20,
                moment=50,
                body_type=pymunk.Body.DYNAMIC
            )

            body.position = pygame.mouse.get_pos()
        
            shape=pymunk.Poly.create_box(
                body=body,
                size=(20,20)
            )

            shape.friction = 0.5
            shape.elasticity = 0.1
            
            tile = ConnectableTile(
                body=body,
                shape=shape,
                game=self,
                updater=self.uuid
            )

            self.last_spawn = time.time()

        if pygame.key.get_pressed()[pygame.K_q]:
            
            body=pymunk.Body(
                mass=20,
                moment=1,
                body_type=pymunk.Body.STATIC
            )

            body.position = pygame.mouse.get_pos()
        
            shape=pymunk.Poly.create_box(
                body=body,
                size=(20,20)
            )

            shape.collision_type = 2

            shape.friction = 0.5
            shape.elasticity = 0.1
            
            tile = Tile(
                body=body,
                shape=shape,
                game=self,
                updater=self.uuid
            )

            print(shape.friction)

            self.last_spawn = time.time()


    def start(self, event: GameStart):
        
        tile_maker = ConnectableTileMaker(self,self.uuid)

        

