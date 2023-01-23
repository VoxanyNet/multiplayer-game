import uuid

import pygame.key

from engine import Entity, Unresolved


class Weapon(Entity):
    def __init__(self, wielder=None, damage=None, attack_speed=None, rect=None, game=None, updater=None, uuid=str(uuid.uuid4()),
                 sprite_path=None, scale_res=None, visible=True):

        # initialize base entity
        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

        # checking for required arguments
        if wielder is None:
            raise AttributeError("Missing wielder argument")

        if damage is None:
            raise AttributeError("Missing damage argument")

        if attack_speed is None:
            raise AttributeError("Missing attack_speed argument")

        self.wielder = wielder
        self.damage = damage
        self.attack_speed = attack_speed

    def dict(self):
        # create a json serializable dictionary with all of this object's attributes

        # create the base entity's dict, then we add our own unique attributes on top
        data_dict = super().dict()

        data_dict.update(
            {
                "wielder": self.wielder.uuid,
                "damage": self.damage,
                "attack_speed": self.attack_speed
            }
        )

        return data_dict

    @classmethod
    def create(cls, entity_data, entity_id, game):
        # convert json entity data to object constructor arguments

        entity_data["wielder"] = Unresolved(entity_data["wielder"])

        entity_data["damage"] = entity_data["damage"]

        entity_data["attack_speed"] = entity_data["attack_speed"]

        # base entity create method will extract the data it needs from the dictionary, then create the object
        new_player = super().create(entity_data, entity_id, game)

        return new_player

    def update(self, update_data):
        # update the attributes of this object with update data

        # update base entity attributes
        super().update(update_data)

        # loop through every attribute being updated
        for attribute in update_data:

            # we only need to check for attribute updates unique to this entity
            match attribute:

                case "wielder":
                    self.wielder = Unresolved(update_data["wielder"])

                case "damage":
                    self.damage = update_data["damage"]

                case "attack_speed":
                    self.attack_speed = update_data["attack_speed"]

    def tick(self):
        # code to run every game tick

        keys = pygame.key.get_pressed()

        pass
