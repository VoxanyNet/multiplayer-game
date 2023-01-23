from pygame import Rect
from pygame import mouse

from weapon import Weapon


class Sword(Weapon):

    def attack(self):
        # create vectors that shoot from player towards mouse

        mouse_pos = mouse.get_pos()

        path = (
            self.rect.x - mouse_pos[0],
            self.rect.y - mouse_pos[1]
        )
