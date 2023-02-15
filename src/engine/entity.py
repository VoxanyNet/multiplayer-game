import uuid

import pygame.image
from pygame import Rect

from engine.unresolved import Unresolved
from engine.helpers import get_matching_objects
from engine.events import TickEvent


class Entity:
    def __init__(self, rect=None, game=None, updater=None, uuid=str(uuid.uuid4()), sprite_path=None, scale_res=None,
                 visible=True):

        if rect is None:
            raise TypeError("Missing rect argument")

        if game is None:
            raise TypeError("Missing game argument")

        if updater is None:
            raise TypeError("Missing updater argument")

        self.visible = visible
        self.rect = rect
        self.updater = updater
        self.uuid = uuid
        self.game = game
        self.sprite_path = sprite_path
        self.scale_res = scale_res

        self.game.entities[self.uuid] = self

        if sprite_path:
            self.sprite = pygame.image.load(sprite_path)

        if scale_res and sprite_path:
            print("scaling")
            self.sprite = pygame.transform.scale(self.sprite, scale_res)

        self.game.event_subscriptions[TickEvent].append(self.tick)

    def resolve(self):
        for attribute_name, attribute in self.__dict__.copy().items():

            if type(attribute) is not Unresolved:
                continue

            resolved_attribute = self.game.entities[
                attribute.uuid
            ]

            self.__setattr__(attribute_name, resolved_attribute)

    def dict(self):

        data_dict = {
            "rect": list(self.rect),
            "visible": self.visible,
            "updater": self.updater,
            "sprite_path": self.sprite_path,
            "scale_res": self.scale_res
        }

        return data_dict

    @classmethod
    def create(cls, entity_data, entity_id, game):

        entity_data["rect"] = Rect(
            entity_data["rect"]
        )

        entity_data["visible"] = entity_data["visible"]

        entity_data["updater"] = entity_data["updater"]

        entity_data["sprite_path"] = entity_data["sprite_path"]

        entity_data["scale_res"] = entity_data["scale_res"]

        return cls(game=game, uuid=entity_id, **entity_data)

    def update(self, update_data):

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

    def tick(self, event):
        pass

    def draw(self):
        self.game.screen.blit(self.sprite, self.rect)
