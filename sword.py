from pygame import Rect
from pygame import mouse

from weapon import Weapon

class Sword(Weapon):
    def __init__(self, game, updater, wielder, damage=30, attack_speed=0.5, rect=Rect(0, 0, 20, 20),):
        super().__init__(rect, game, updater, wielder, damage, attack_speed)

    def attack(self):
        # create vectors that shoot from player towards mouse

        mouse_pos = mouse.get_pos()

        path = (
            self.rect.x - mouse_pos[0],
            self.rect.y - mouse_pos[1]
        )
