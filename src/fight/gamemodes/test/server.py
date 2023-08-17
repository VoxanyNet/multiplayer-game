import time
import uuid
import socket 

from pygame import Rect
import pymunk

from engine.gamemode_server import GamemodeServer
from engine.tile import Tile
from engine.events import ServerStart
from fight.gamemodes.test.entities import ConnectableTile, ConnectableTileMaker

class Server(GamemodeServer):
    def __init__(self, server_ip: str = socket.gethostname(), server_port: int = 5560, network_compression: bool = True):
        super().__init__( server_ip=server_ip, server_port=server_port, network_compression=network_compression)

        self.entity_type_map.update(
            {
                "connectable_tile": ConnectableTile,
                "connectable_tile_maker": ConnectableTileMaker
            }
        )

        self.event_subscriptions[ServerStart] += [
            self.start
        ]
    
    def start(self, event: ServerStart):

        pass
        