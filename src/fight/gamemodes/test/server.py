import time
import uuid
import socket 

from pygame import Rect

from engine.gamemode_server import GamemodeServer
from engine.events import ServerStart
from fight.gamemodes.test.entities import TestDynamic

class TestServer(GamemodeServer):
    def __init__(self, tick_rate, server_ip: str = socket.gethostname(), server_port: int = 5560):
        super().__init__(tick_rate=tick_rate, server_ip=server_ip, server_port=server_port)

        self.entity_type_map.update(
            {
                "test_dynamic": TestDynamic
            }
        )

        self.event_subscriptions[ServerStart] += [
            self.start
        ]
    
    def start(self, event: ServerStart):

        pass
        