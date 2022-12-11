from pygame import mouse

from engine import Entity


class Weapon(Entity):
    def __init__(self, rect, wielder, game, updater, damage, attack_speed):
        super().__init__(rect, game, updater)

        # the player entity that is using this weapon
        self.wielder = wielder
        self.damage = damage
        self.attack_speed = attack_speed

    def tick(self):

        clicked = mouse.get_pressed()

        # calls this weapon's attack function when the left mouse button is clicked
        if clicked[1]:
            self.attack()

