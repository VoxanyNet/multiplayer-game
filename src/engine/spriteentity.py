from typing import Union, Tuple, TYPE_CHECKING

import pygame
from pygame import Rect

from engine.entity import Entity

if TYPE_CHECKING:
    from engine.gamemode_client import GamemodeClient
    from engine.gamemode_server import GamemodeServer

class SpriteEntity(Entity):
    """An entity that is represented with a sprite"""
    def __init__(self, sprite_path: str, interaction_rect: Rect, draw_rect: Rect, game: Union["GamemodeClient", "GamemodeServer"], updater: str, id: str, scale_res: Tuple[int, int] = None, visible=True):
        
        self.sprite_path = sprite_path
        self.visible = visible
        self.draw_rect = draw_rect # the rectange used to draw the sprite onto the screen
        
        if sprite_path:
            self.sprite = pygame.image.load(sprite_path)

        if scale_res and sprite_path:
            self.sprite = pygame.transform.scale(self.sprite, scale_res)
        
        super().__init__(interaction_rect=interaction_rect, game=game, updater=updater, id=id)
    
    def draw(self):
        self.game.screen.blit