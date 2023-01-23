from pygame import Rect

from engine import Game
from player import Player
from weapon import Weapon
from sword import Sword


class Fight(Game):
    def __init__(self, fps=60):
        super().__init__(fps=fps)

        self.entity_type_map.update(
            {
                "player": Player,
                "weapon": Weapon,
                "sword": Sword
            }
        )
    
    def start(self, server_ip, server_port=5560):
        super().start(server_ip=server_ip,server_port=server_port)

        # create our player object
        player = Player(health=100,
            weapon=None,
            rect=Rect(500,500,200,200),
            game=self,
            updater=self.uuid,
            sprite_path="resources/player.png",
            scale_res=(1,1),
            visible=True
        )

        print(self.lookup_entity_type_string(player))
        
        self.network_update(
            update_type="create",
            entity_id=player.uuid,
            data=player.dict(),
            entity_type=self.lookup_entity_type_string(player)
        )

        weapon = Weapon(wielder=player,damage=20,attack_speed=5,rect=Rect(50,50,50,50),game=self,updater=self.uuid,sprite_path="resources/player.png")

        self.network_update(
            update_type="create",
            entity_id=weapon.uuid,
            data=weapon.dict(),
            entity_type=self.lookup_entity_type_string(weapon)
        )

        player.weapon = weapon 
        
        self.network_update(
            update_type="update",
            entity_id=player.uuid,
            data = {
                "weapon": weapon.uuid
            }
        )

        


