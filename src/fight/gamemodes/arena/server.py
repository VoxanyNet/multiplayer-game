import time
import uuid
import socket 

from pygame import Rect

from engine.gamemode_server import GamemodeServer
from engine.events import ServerStart
from fight.gamemodes.arena.entities import Player, Floor, Shotgun, Portal, Wall

class ArenaServer(GamemodeServer):
    def __init__(self, tick_rate, server_ip: str = socket.gethostname()):
        super().__init__(tick_rate=tick_rate)

        self.entity_type_map.update(
            {
                "player": Player,
                "floor": Floor,
                "shotgun": Shotgun,
                "portal": Portal,
                "wall": Wall
            }
        )

        self.event_subscriptions[ServerStart] += [
            self.start
        ]
    
    def start(self, event: ServerStart):

        floor = Floor(
            interaction_rect=Rect(0,600,1920,20),
            game=self,
            updater="server",
            id=str(uuid.uuid4())
        )

        portal = Portal(
            interaction_rect=Rect(600, 400, 20, 200),
            game=self,
            updater="server",
            id=str(uuid.uuid4())
        )

        wall = Wall(
            interaction_rect=Rect(610, 400, 20, 200),
            game=self,
            updater="server",
            id=str(uuid.uuid4())
        )
        