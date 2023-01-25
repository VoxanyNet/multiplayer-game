from pygame import Rect

from engine import Game
from player import Player
from weapon import Weapon
from sword import Sword
from floor import Floor
from cursor import Cursor


class Fight(Game):
    def __init__(self, fps=60):
        super().__init__(fps=fps)

        self.entity_type_map.update(
            {
                "player": Player,
                "weapon": Weapon,
                "sword": Sword,
                "floor": Floor,
                "cursor": Cursor
            }
        )
    
    def start(self, server_ip, server_port=5560):
        super().start(server_ip=server_ip,server_port=server_port)

        cursor = Cursor(
            rect=Rect(0,0,10,10),
            game=self,
            updater=self.uuid
        )

        self.network_update(
            update_type="create",
            entity_id=cursor.uuid,
            data=cursor.dict(),
            entity_type="cursor"
        )

        


