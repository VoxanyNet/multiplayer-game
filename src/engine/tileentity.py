from typing import Union, TypedDict, Type, Literal, Dict, List, TYPE_CHECKING

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
    body_type: Union[Literal["dynamic"], Literal["static"], Literal["kinematic"]]

class TileEntity(Entity):
    """An entity that is composed of physics tiles"""
    def __init__(self, origin, tile_layout: List[dict], interaction_rect: Rect,  game: Union["GamemodeClient", "GamemodeServer"], updater: str, id: str, visible=True):
        
        super().__init__(interaction_rect=interaction_rect, game=game, updater=updater, id=id)
        
        self.visible = visible
        self.origin = origin

        self.tiles: List[Tile] = []

        self._load_tile_layout(tile_layout=tile_layout, origin=origin)

        print(f"new tile entity!! {self.serialize(is_new=True)}")
    
    def serialize(self, is_new: bool):
        data_dict = super().serialize(is_new)


        data_dict.update(
            {
                "visible": self.visible,
                "origin": self.origin 
            }
        )

        if is_new:
            # this is the main reason i added the is_new parameter. sending this data every tick takes a lot of bandwith

            # serialize tile layout
            tile_layout: List[TileDict] = []

            for tile in self.tiles:
                
                # if tile.body.body_type is pymunk.Body.DYNAMIC:
                #     body_type_string = "dynamic"
                # elif tile.body.body_type is pymunk.Body.STATIC:
                #     body_type_string = "static"
                # elif tile.body.body_type is pymunk.Body.KINEMATIC:
                #     body_type_string = "kinematic"

                tile_layout.append(
                    {
                        "height": tile.shape.bb.top - tile.shape.bb.bottom, # y value increases as height decreases
                        "width": tile.shape.bb.right - tile.shape.bb.left,
                        "mass": tile.body.mass,
                        "moment": tile.body.moment,
                        "x": tile.body.position.x,
                        "y": tile.body.position.y,
                        #"body_type": body_type_string
                    }        
                )
            
            data_dict.update(
            {
                "tile_layout": tile_layout
            }
        )

            

        return data_dict

    @classmethod
    def create(cls, entity_data: Dict[str, Union[int, bool, str, list]], entity_id: str, game: Union["GamemodeClient", "GamemodeServer"]) -> Type["TileEntity"]:
        """Translate serialized entity data into an actual TileEntity object"""

        entity_data["origin"] = entity_data["origin"]

        entity_data["tile_layout"] = entity_data["tile_layout"]

        # call the base entity create method to do its own stuff and then return the actual object
        new_player = super().create(entity_data, entity_id, game)

        return new_player

    def update(self, update_data: Dict):

        super().update(update_data)

        # loop through every attribute being updated
        # for attribute in update_data:

        #     match attribute:

        #         case "example":
        #             self.example = update_data["example"]

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