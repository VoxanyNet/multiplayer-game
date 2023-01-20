from engine import Game
from player import Player
from weapon import Weapon
from sword import Sword


class Fight(Game):
    def __init__(self, fps=60, is_server=False):
        super().__init__(fps=fps, is_server=is_server)

        self.entity_type_map.update(
            {
                "player": Player,
                "weapon": Weapon,
                "sword": Sword
            }
        )
