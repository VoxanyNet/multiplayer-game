import uuid

import pygame
import pygame.key

from engine.entity import Entity 
from engine.events import TickEvent


class Cursor(Entity):
    def __init__(self, draw_pos=(10,10), game=None, updater=None, uuid=str(uuid.uuid4()),
                 sprite_path="./resources/square.png", scale_res=None, visible=True):

        super().__init__(draw_pos=draw_pos, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

        self.game.event_subscriptions[TickEvent].append(self.update_position)

    def update_position(self, event):

        self.draw_pos = pygame.mouse.get_pos()
