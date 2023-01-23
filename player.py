import uuid

import pygame.key

from engine import Entity, Unresolved


class Player(Entity):
    def __init__(self, health=100, weapon=None, rect=None, game=None, updater=None, uuid=str(uuid.uuid4()),
                 sprite_path=None, scale_res=None, visible=True):

        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

        # the last time this player used a weapon
        self.last_attack = 0

        if health is None:
            raise AttributeError("Missing health argument")

        self.health = health
        self.weapon = weapon

    def dict(self):
        # create a json serializable dictionary with all of this object's attributes

        # create the base entity's dict, then we add our own unique attributes on top
        data_dict = super().dict()

        data_dict["health"] = self.health

        # since this attribute can be two different types, we need to check
        if self.weapon is not None:
            data_dict["weapon"] = self.weapon.uuid
        else:
            data_dict["weapon"] = None

        return data_dict

    @classmethod
    def create(cls, entity_data, entity_id, game):
        # convert json entity data to object constructor arguments

        entity_data["health"] = entity_data["health"]

        # when network updates need to reference other objects, we use its uuid
        if entity_data["weapon"] is not None:
            entity_data["weapon"] = Unresolved(entity_data["weapon"])
        else:
            entity_data["weapon"] = None

        # call the base entity create method to do its own stuff and then return the actual object!!!!!
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

                case "health":
                    self.health = update_data["health"]

                case "weapon":
                    # okay so this is kinda confusing
                    # if you wanted to update the weapon object you would send an update for the weapon itself, not the player
                    # the only case in which you would update the weapon on the player side is if the weapon has been changed or removed

                    if update_data["weapon"] is not None:
                        self.weapon = Unresolved(update_data["weapon"])
                    else:
                        self.weapon = None

    def tick(self):
        keys = pygame.key.get_pressed()

        #print(keys)
