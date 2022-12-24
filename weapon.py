import uuid

from pygame import mouse

from engine import Entity, Unresolved


#def __init__(self, rect, game, updater, uuid=str(uuid.uuid4()), sprite_path=None, scale_res=None):
class Weapon(Entity):

    def __init__(self, rect, wielder, game, updater, damage, attack_speed, uuid=str(uuid.uuid4())):
        super().__init__(rect, game, updater, uuid)

        # the player entity that is using this weapon
        self.wielder = wielder
        self.damage = damage
        self.attack_speed = attack_speed
    
    @staticmethod
    def create(update_data, game):

        # construct a rect object from the list of values
        rect = Rect(
            update_data["rect"][0],
            update_data["rect"][1],
            update_data["rect"][2],
            update_data["rect"][3]
        )
        updater = update_data["updater"]
        sprite_path = update_data["sprite_path"]

        wielder = Unresolved(update_data["wielder"])
        damage = update_data["damage"]
        attack_speed = update_data["attack_speed"]

        new_weapon = Weapon(rect=rect,updater=updater,sprite_path=sprite_path,wielder=wielder,damage=damage,
            attack_speed=attack_speed)

        return new_weapon

    def update(self, update_data):
        super().update(update_data)

        for attribute in update_data:

            match attribute:
                case "wielder":
                    self.wielder = Unresolved(update_data["wielder"])
                case "damage":
                    self.damage = update_data["damage"]
                case "attack_speed":
                    self.attack_speed = update_data["attack_speed"]

    def attack(self):
        # the base weapon object does nothing

        pass 

    def tick(self):

        clicked = mouse.get_pressed()

        # calls this weapon's attack function when the left mouse button is clicked
        if clicked[1]:
            self.attack()

