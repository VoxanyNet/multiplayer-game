import uuid

import pygame.image

from engine import Unresolved


class Entity:
    def __init__(self, rect, game, updater, uuid=str(uuid.uuid4()), sprite_path=None, scale_res=None):

        # if we should blit this entity's sprite
        self.visible = True

        self.rect = rect
        # the uuid for the game that will update this entity every tick
        self.updater = updater
        # this uuid is used to distinguish itself from other entities within the game
        self.uuid = uuid
        # the entity's game object
        self.game = game

        # adds this entity to the list of game entities
        self.game.entities[self.uuid] = self

        # if a sprite path was not provided, then we make the entity invisible
        if not sprite_path:
            self.visible = False

            # load an image as a sprite
            self.sprite = pygame.image.load(sprite_path)

        # only scale the sprite if an image was passed
        if sprite_path and scale_res:
            self.sprite = pygame.transform.scale(self.sprite, scale_res)

    def resolve(self):
        # resolve entity ids to their actual objects
        for attribute in self.__dict__.values():

            if type(attribute) is not Unresolved:
                continue

            print(f"Resolving entity {attribute.uuid}")

            # replace the attribute with the actual entity object
            attribute = self.game.entities[
                attribute.uuid
            ]

    def dict(self):
        # create a json serializable dictionary with all of this object's attributes

        # create the base entity's dict, then we add our own unique attributes on top
        data_dict = super().dict()

        data_dict.update(
            {
                "example1": self.exampele1,
                "example2": self.example2
            }
        )

    @staticmethod
    def create(update_data, entity_id, game):
        # return a new entity using a dict of data

        # we cant inherit the create function because reasons

        pass

    def update(self, update_data):

        super().update(update_data)

        # loop through every attribute being updated
        for attribute in update_data:

            match attribute:

                case "example1":
                    self.example1 = update_data["example1"]

                case "example2":
                    self.example2 = update_data["example2"]

    def tick(self):
        # this function runs every tick

        super().tick()

        # do entity specific operations here
        pass
