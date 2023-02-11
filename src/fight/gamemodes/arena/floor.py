import uuid

import pygame.key

from engine.entity import Entity

class Floor(Entity):
    def __init__(self, draw_pos=None, game=None, updater=None, uuid=str(uuid.uuid4()),
                 sprite_path=None, scale_res=None, visible=True):

        super().__init__(draw_pos=draw_pos, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

    def dict(self):

        data_dict = super().dict()

        return data_dict

    @classmethod
    def create(cls, entity_data, entity_id, game):

        new_player = super().create(entity_data, entity_id, game)

        return new_player

    def update(self, update_data):

        super().update(update_data)

        for attribute in update_data:

            match attribute:

                case "test":
                    pass

    def tick(self, trigger_entity=None):
        super().tick(trigger_entity=trigger_entity)
