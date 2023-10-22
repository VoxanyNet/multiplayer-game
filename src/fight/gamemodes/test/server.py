import time
import uuid
import socket 

from pygame import Rect
import pymunk
from pymunk import Body

from engine.gamemode_server import GamemodeServer
from engine.tile import Tile
from engine.events import ServerStart
from fight.gamemodes.test.entities import FreezableTile, FreezableTileMaker, Weapon, Player, Bullet
from fight.gamemodes.test.entity_type_map import entity_type_map

class Server(GamemodeServer):
    def __init__(self, server_ip: str = socket.gethostname(), server_port: int = 5560, network_compression: bool = True):
        super().__init__(server_ip=server_ip, server_port=server_port, network_compression=network_compression)

        self.entity_type_map.update(
            entity_type_map
        )

        self.event_subscriptions[ServerStart] += [
            self.start
        ]

        self.boundry_rect = boundry_rect = Rect(0,0,1280,720)
    
    def start(self, event: ServerStart):
        
        floor_body = Body(body_type=pymunk.Body.STATIC)
        floor_shape=pymunk.Poly.create_box(body=floor_body,size=(1000,20))
        floor_shape.friction = 1
        floor_body.position = (self.boundry_rect.centerx, self.boundry_rect.bottom - 10)
        floor = Tile(body=floor_body, game=self, shape=floor_shape, updater=self.uuid)
        