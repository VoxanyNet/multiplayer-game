import uuid

import pygame.key
from pygame import Rect

from engine import Entity, Unresolved


class Player(Entity):
    def __init__(self, rect, game, updater, weapon, uuid=str(uuid.uuid4()), sprite_path=None, health=100):
        super().__init__(rect, game, updater, sprite_path)

        # the last time this player used a weapon
        self.last_attacked = 0

        self.health = health
        self.weapon = weapon

    def dict(self):
        # create a json serializable dictionary with all of this object's attributes

        # create the base entity's dict, then we add our own unique attributes on top
        data_dict = super().dict()

        data_dict.update(
            {
                "health": self.health,
                "weapon": self.weapon.uuid  # this will be resolved to the actual object on the client
            }
        )

    @staticmethod
    def create(update_data, entity_id, game):
        # create a new player entity using update data dict

        # we need to extract base entity attributes as well player attributes because reasons

        # construct a rect object from the list of values
        rect = Rect(
            update_data["rect"][0],
            update_data["rect"][1],
            update_data["rect"][2],
            update_data["rect"][3]
        )
        updater = update_data["updater"]
        sprite_path = update_data["sprite_path"]
        health = update_data["health"]
        # when network updates need to reference other objects, we use its uuid
        weapon = Unresolved(update_data["weapon"])

        # create the actual player object
        new_player = Player(rect=rect, game=game, updater=updater, weapon=weapon, sprite_path=sprite_path,
                            health=health, uuid=entity_id)

        return new_player

    def update(self, update_data):
        # update the attributes of this object with update data

        # update base entity attributes
        super().update(update_data)

        # loop through every attribute being updated
        for attribute in update_data:

            # we only need to check for attribute updates unique to this entity
            match attribute:

                case "health":
                    self.health = update_data["health"]

                case "weapon":
                    self.weapon = Unresolved(update_data["weapon"])

    def tick(self):
        keys = pygame.key.get_pressed()

        print(keys)
