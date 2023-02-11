from engine.gamemode_server import GamemodeServer
from fight.gamemodes.arena.player import Player
from fight.gamemodes.arena.floor import Floor

class ArenaServer(GamemodeServer):
    def __init__(self, tick_rate):
        super().__init__(tick_rate=tick_rate)

        self.entity_type_map.update(
            {
                "player": Player,
                "floor": Floor
            }
        )
    
    def start(self, host, port):

        super().start(host, port)



        
