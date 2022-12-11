from pygame import Rect

from engine import Entity, Unresolved


class Player(Entity):
    def __init__(self, rect, game, updater, weapon, sprite_path=None, health=100):
        super().__init__(rect, game, updater, sprite_path)

        # the last time this player used a weapon
        self.last_attacked = 0

        self.health = health
        self.weapon = weapon

    @staticmethod
    def create(self, update_data):
        # create a new player entity using update data dict

        # construct a rect object from the list of values
        rect = Rect(
            update_data["rect"][0],
            update_data["rect"][1],
            update_data["rect"][2],
            update_data["rect"][3]
        )
        game = self.game
        updater = update_data["updater"]
        health = update_data["health"]
        # when network updates need to reference other objects, we use its uuid
        weapon = Unresolved(update_data["weapon"])

