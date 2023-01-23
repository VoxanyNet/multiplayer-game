from engine.game_server import GameServer
from player import Player
from weapon import Weapon
from sword import Sword

from pygame import Rect

class FightServer(GameServer):
    def __init__(self):
        super().__init__()

        self.entity_type_map.update(
            {
                "player": Player,
                "weapon": Weapon,
                "sword": Sword
            }
        )
    
    def start(self, host, port):
        
        player = Player(health=100,weapon=None,rect=Rect(1,1,1,1),game=self,updater="server",sprite_path="resources/player.png")

        super().start(host, port)



        
