import time
import uuid
import socket 

from pygame import Rect
import pymunk

from engine.gamemode_server import GamemodeServer
from engine.tile import Tile
from engine.events import ServerStart

class TestServer(GamemodeServer):
    def __init__(self, server_ip: str = socket.gethostname(), server_port: int = 5560, network_compression: bool = True):
        super().__init__( server_ip=server_ip, server_port=server_port, network_compression=network_compression)

        self.entity_type_map.update(
            {
            }
        )

        self.event_subscriptions[ServerStart] += [
            self.start
        ]
    
    def start(self, event: ServerStart):

        pass
        