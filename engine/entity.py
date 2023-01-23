import uuid

import pygame.image
from pygame import Rect

from .unresolved import Unresolved


class Entity:
    def __init__(self, rect=None, game=None, updater=None, uuid=str(uuid.uuid4()), sprite_path=None, scale_res=None,
                 visible=True):

        # check for required arguments
        if rect is None:
            raise TypeError("Missing rect argument")

        if game is None:
            raise TypeError("Missing game argument")

        if updater is None:
            raise TypeError("Missing updater argument")

        if visible and sprite_path is None:
            raise TypeError("Missing sprite_path argument")

        # if we should blit this entity's sprite
        self.visible = visible

        self.rect = rect
        # the uuid for the game that will update this entity every tick
        self.updater = updater
        # this uuid is used to distinguish itself from other entities within the game
        self.uuid = uuid
        # the entity's game object
        self.game = game
        self.sprite_path = sprite_path
        self.scale_res = scale_res

        # adds this entity to the list of game entities
        self.game.entities[self.uuid] = self

        # if a sprite path was not provided, then we make the entity invisible
        if not sprite_path:
            self.visible = False

        else:

            # load an image as a sprite
            self.sprite = pygame.image.load(sprite_path)

            # only scale the sprite if an image was passed
            if sprite_path and scale_res:
                self.sprite = pygame.transform.scale(self.sprite, scale_res)

    def resolve(self):
        # resolve entity ids to their actual objects
        for attribute_name, attribute in self.__dict__.copy().items():

            if type(attribute) is not Unresolved:
                continue

            print(f"Resolving entity {attribute.uuid}")

            # fetch the actual entity
            resolved_attribute = self.game.entities[
                attribute.uuid
            ]

            # update the attribute with actual entity
            self.__setattr__(attribute_name, resolved_attribute)

    def dict(self):
        # dump just the base entity attributes to a dict

        data_dict = {
            "rect": [
                self.rect.x,
                self.rect.y,
                self.rect.width,
                self.rect.height
            ],
            "visible": self.visible,
            "updater": self.updater,
            "sprite_path": self.sprite_path,
            "scale_res": self.scale_res
        }

        return data_dict

    @classmethod
    def create(cls, entity_data, entity_id, game):
        # convert all the attributes in the entity_data dictionary to the proper argument forms
        # that explanation makes zero sense

        entity_data["rect"] = Rect(
            entity_data["rect"]
        )

        # this is really stupid but, I just want to illustrate what we are doing here
        entity_data["visible"] = entity_data["visible"]

        entity_data["updater"] = entity_data["updater"]

        entity_data["sprite_path"] = entity_data["sprite_path"]

        entity_data["scale_res"] = entity_data["scale_res"]

        # pass the entity_data dictionary as keyword arguments to the object constructor
        return cls(game=game, uuid=entity_id, **entity_data)

    def update(self, update_data):

        # loop through every attribute being updated
        for attribute in update_data:

            match attribute:

                case "visible":
                    self.visible = update_data["visible"]

                case "rect":
                    self.rect.update(
                        update_data["rect"]
                    )

                case "updater":
                    self.updater = update_data["updater"]

                case "sprite_path":
                    self.sprite = pygame.image.load(update_data["sprite_path"])

    def tick(self):
        # this function runs every tick
        pass
