import uuid

import pymunk

from engine.vector import Vector
from engine.entity import Entity
from engine.events import TickEvent
from engine.events import LandedEvent

class PhysicsEntity(Entity):
    def __init__(self, draw_pos=None, game=None, updater=None, uuid=str(uuid.uuid4()), sprite_path=None, scale_res=None, visible=True):

        super().__init__(draw_pos=draw_pos, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res, visible=visible)
        
        self.body = pymunk.Body()

        self.game.event_subscriptions[TickEvent] += [
            self.update_pos
        ]

    def update_pos(self, event):
        self.draw_pos = self.body.position

    def dict(self):

        data_dict = super().dict()

        return data_dict
    
    @classmethod
    def create(cls, entity_data, entity_id, game):

        new_player = super().create(entity_data, entity_id, game)

        return new_player
    
    def update(self, update_data):

        super().update(update_data)

        # loop through every attribute being updated
        for attribute in update_data:

            match attribute:

                case "velocity":
                    pass