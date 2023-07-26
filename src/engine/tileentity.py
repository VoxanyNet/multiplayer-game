from typing import Union, List, TYPE_CHECKING

from pygame import Rect
import pygame
import pymunk

from engine.entity import Entity
from engine.tile import Tile    

if TYPE_CHECKING:
    from engine.gamemode_client import GamemodeClient
    from engine.gamemode_server import GamemodeServer

class TileEntity(Entity):
    """An entity that is composed of physics tiles"""
    def __init__(self, interaction_rect: Rect, game: Union["GamemodeClient", "GamemodeServer"], updater: str, id: str, visible=True):
        
        super().__init__(interaction_rect=interaction_rect, game=game, updater=updater, id=id)
        
        self.visible = visible

        self.tiles: List[Tile] = []


    
    def draw(self):
        print(self.tiles[0].body.position.x)
        print(self.tiles[0].body.position.y)
        pygame.draw.rect(
            self.game.screen,
            (255,255,255),
            [
                self.tiles[0].body.position.x,
                self.tiles[0].body.position.y,
                20,
                20
            ]
        )