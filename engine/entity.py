import uuid

import pygame.image

from engine import Unresolved


class Entity:
    def __init__(self, rect, game, updater, sprite_path=None, scale_res=None):

        # if we should blit this entity's sprite
        self.visible = True

        self.rect = rect
        # the uuid for the game that will update this entity every tick
        self.updater = updater
        # this uuid is used to distinguish itself from other entities within the game
        self.uuid = str(uuid.uuid4())
        # the game object that created this entity
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

    @staticmethod
    def create(self, update_data):
        # return a new entity using a dict of data

        pass

    def tick(self):
        # this function runs every tick
        pass
