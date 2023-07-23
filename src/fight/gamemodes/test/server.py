import time
import uuid
import socket 

from pygame import Rect

from engine.gamemode_server import GamemodeServer
from engine.events import ServerStart
from fight.gamemodes.arena.entities import Player, Floor, Shotgun, Cursor, Portal, Wall

class TestServer(GamemodeServer):
    def __init__(self, tick_rate, server_ip: str = socket.gethostname()):
        super().__init__(tick_rate=tick_rate, server_ip=server_ip)

        self.entity_type_map.update(
            {
            }
        )

        self.event_subscriptions[ServerStart] += [
            self.start
        ]
    
    def start(self, event: ServerStart):

        pass
        