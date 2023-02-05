from pygame import Rect

from engine.game_server import GameServer
from player import Player
from floor import Floor

class FightServer(GameServer):
    def __init__(self, tick_rate):
        super().__init__(tick_rate=tick_rate)

        self.entity_type_map.update(
            {
                "player": Player,
                "floor": Floor
            }
        )
    
    def start(self, host, port):

        floor = Floor(
            rect=Rect(0,600,1920,20),
            game=self,
            updater="server"
        )

        super().start(host, port)



        
