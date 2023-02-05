import uuid

import pygame
import pygame.key
from pygame import Rect

from engine.entity import Entity 
from engine.unresolved import Unresolved
from engine.physics_entity import PhysicsEntity
from engine.vector import Vector
from engine.events import TickEvent


class Cursor(Entity):
    def __init__(self, rect=Rect(0,0,10,10), game=None, updater=None, uuid=str(uuid.uuid4()),
                 sprite_path=None, scale_res=None, visible=True):

        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

        self.game.event_subscriptions[TickEvent].append(self.update_position)
    
    def draw(self):

        pygame.draw.rect(
            self.game.screen,
            (255,255,255),
            self.rect
        )

    def update_position(self, event):

        self.rect.center = pygame.mouse.get_pos()
