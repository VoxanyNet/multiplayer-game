from typing import Union, TypedDict, Dict, List, TYPE_CHECKING

from pygame import Rect
import pygame
import pymunk

from engine.entity import Entity
from engine.tile import Tile    

if TYPE_CHECKING:
    from engine.gamemode_client import GamemodeClient
    from engine.gamemode_server import GamemodeServer

class TileDict(TypedDict):
    x: float
    y: float 
    width: float 
    height: float
    mass: float 
    moment: float

class TileEntity(Entity):
    """An entity that is composed of physics tiles"""
    def __init__(self, origin, tile_layout: List[dict], interaction_rect: Rect,  game: Union["GamemodeClient", "GamemodeServer"], updater: str, id: str, visible=True):
        
        super().__init__(interaction_rect=interaction_rect, game=game, updater=updater, id=id)
        
        self.visible = visible
        self.origin = origin

        self.tiles: List[Tile] = []

        self._load_tile_layout(tile_layout=tile_layout, origin=origin)
    
    def dict(self):
        data_dict = super().dict()

        # serialize tile layout
        tile_layout: List[TileDict] = []

        for tile in self.tiles:
            tile_layout.append(
                {
                    "height": tile.shape.bb.bottom - tile.shape.bb.top, # y value increases as height decreases
                    "width": tile.shape.bb.right - tile.shape.bb.left,
                    "mass": tile.body.mass,
                    "moment": tile.body.moment,
                    "x": tile.body.position.x,
                    "y": tile.body.position.y
                }        
            )

        data_dict.update(
            {
                "visible": self.visible,
                "tile_layout": tile_layout,
                "origin": self.origin 
            }
        )

        return data_dict

    def _load_tile_layout(self, tile_layout: List[TileDict], origin: List[int]):
        """Load a serialized tile layout into a list of actual tiles"""

        for tile_dict in tile_layout:
            
            body = pymunk.Body(
                mass=tile_dict["mass"],
                moment=tile_dict["moment"],

            )

            body.position = [
                origin[0] + tile_dict["x"],
                origin[1] + tile_dict["y"]
            ]
            
            shape = pymunk.Poly.create_box(
                body=body,
                size=[
                    tile_dict["width"],
                    tile_dict["height"]
                ]
            )

            tile = Tile(entity=self, body=body, shape=shape)

            self.tiles.append(tile)
    
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