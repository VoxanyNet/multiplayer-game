from pygame import Rect

from engine.gamemode_server import GamemodeServer
from fight.gamemodes.arena.player import Player
from fight.gamemodes.arena.floor import Floor
from fight.gamemodes.arena.shotgun import Shotgun

class ArenaServer(GamemodeServer):
    def __init__(self):
        super().__init__()

        self.entity_type_map.update(
            {
                "player": Player,
                "floor": Floor,
                "shotgun": Shotgun
            }
        )



        