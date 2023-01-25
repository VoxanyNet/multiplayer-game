from engine import GameServer
from player import Player
from weapon import Weapon
from sword import Sword
from floor import Floor
from cursor import Cursor

from pygame import Rect

class FightServer(GameServer):
    def __init__(self):
        super().__init__()

        self.entity_type_map.update(
            {
                "player": Player,
                "weapon": Weapon,
                "sword": Sword,
                "floor": Floor,
                "cursor": Cursor
            }
        )
    
    def start(self, host, port):

        floor = Floor(
            rect=Rect(100,100,100,20),
            game=self,
            updater="server"
        )

        super().start(host, port)



        
