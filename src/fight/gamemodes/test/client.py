import socket
import uuid
import time

import pygame
from pygame import Rect
import pymunk
from pymunk import Body, Shape

from engine.gamemode_client import GamemodeClient
from engine.events import GameStart, Tick
from engine import events
from engine.tile import Tile
from fight.gamemodes.test.entities import FreezableTile, FreezableTileMaker, Player, Weapon, Bullet, Background, Shotgun
from fight.gamemodes.test.entity_type_map import entity_type_map

class Client(GamemodeClient):
    def __init__(self, server_ip: str = socket.gethostname(), server_port: int = 5560, network_compression: bool = True):
        super().__init__(server_ip=server_ip, server_port=server_port, network_compression=network_compression)

        self.event_subscriptions[events.KeyE] += [
            self.spawn_entity
        ]

        self.entity_type_map.update(
            entity_type_map
        )

        self.boundry_rect = boundry_rect = Rect(0,0,1280,720)

        #collision_handler = self.space.add_collision_handler(1, 1)

        #collision_handler.begin = collision_callback


        self.last_spawn = 0
    
    def spawn_entity(self, event: events.KeyE):
        
        if time.time() - self.last_spawn < 0.2:
            return
        
        if pygame.key.get_pressed()[pygame.K_e]:
            body=pymunk.Body(
                mass=20,
                moment=50,
                body_type=pymunk.Body.DYNAMIC
            )

            body.position = self.adjusted_mouse_pos
        
            shape=pymunk.Poly.create_box(
                body=body,
                size=(20,20)
            )

            shape.friction = 0.5
            shape.elasticity = 0.1
            
            tile = FreezableTile(
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

            body.position = self.adjusted_mouse_pos
        
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

            self.last_spawn = time.time()


    def start(self, event: GameStart):
        
        tile_maker = FreezableTileMaker(self,self.uuid)

        player = Player(self, updater=self.uuid)

        weapon=Shotgun(self, updater=self.uuid)

        player.weapon = weapon
        weapon.player = player

        background = Background(self, updater=self.uuid)

        # weapon.body.position = (
        #     player.body.position.x + 100,
        #     player.body.position.y + 200
        # )

        # player.weapon = weapon
        # weapon.player = player
        

