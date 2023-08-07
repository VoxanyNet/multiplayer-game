from typing import Dict, Tuple, Union, Type, TYPE_CHECKING

import pymunk
from pygame import Rect
import pygame

from engine.entity import Entity
from engine.unresolved import Unresolved

if TYPE_CHECKING:
    from engine.gamemode_client import GamemodeClient
    from engine.gamemode_server import GamemodeServer

class Tile(Entity):
    def __init__(
            self, 
            body: pymunk.Body,
            shape: pymunk.Shape,
            interaction_rect: Rect, 
            game: Union["GamemodeClient", "GamemodeServer"], 
            updater: str, 
            id: str
        ):

        super().__init__(interaction_rect=interaction_rect, game=game, updater=updater, id=id)

        self.body = body 
        self.shape = shape

        self.game.space.add(self.body, self.shape)
    
    def draw(self):

        vertices = []

        for vertex in self.shape.get_vertices():
            # vertices are not relative to the world, so we need to add the body position
            x = vertex.rotated(self.shape.body.angle)[0] + self.shape.body.position[0]
            y = vertex.rotated(self.shape.body.angle)[1] + self.shape.body.position[1]

            vertices.append((x, y))

        pygame.draw.polygon(
            self.game.screen,
            (255,255,255),
            vertices
        )
    
    def serialize(self, is_new: bool) -> Dict[str, int | bool | str | list]:

        data_dict = super().serialize(is_new)

        if self.body.body_type is pymunk.Body.DYNAMIC:
            body_type_string = "dynamic"
        elif self.body.body_type is pymunk.Body.STATIC:
            body_type_string = "static"
        elif self.body.body_type is pymunk.Body.KINEMATIC:
            body_type_string = "kinematic"
        
        data_dict.update(
            {   
                "body": {
                    "angle": round(self.body.angle, 3),
                    "x": round(self.body.position.x, 3),
                    "y": round(self.body.position.y, 3),
                    "mass": self.body.mass,
                    "moment": self.body.moment,
                    "body_type": body_type_string
                },
                "shape": {
                    "vertices": self.shape.get_vertices(),
                    "friction": self.shape.friction
                }
            }    
        )
            
        #print(data_dict)

        return data_dict
    
    @classmethod
    def create(self, entity_data: Dict[str, Union[int, bool, str, list]], entity_id: str, game: Union["GamemodeClient", "GamemodeServer"]) -> Type["Tile"]:
        """Translate serialized entity data into an actual Tile object"""

        # translate body type string to actual body type
        match entity_data["body"]["body_type"]:
            case "dynamic":
                body_type = pymunk.Body.DYNAMIC
            case "static":
                body_type = pymunk.Body.STATIC
            case "kinematic":
                body_type = pymunk.Body.KINEMATIC
        
        print(entity_data)
        body = pymunk.Body(
            mass=entity_data["body"]["mass"],
            moment=entity_data["body"]["moment"],
            body_type=body_type
        )

        body.position = (entity_data["body"]["x"], entity_data["body"]["y"])

        entity_data["body"] = body

        shape = pymunk.Poly(
            body=body,
            vertices=entity_data["shape"]["vertices"]
        )
        shape.friction = entity_data["shape"]["friction"]

        entity_data["shape"] = shape
        

        return super().create(entity_data, entity_id, game=game)

    def update(self, update_data: dict):

        super().update(update_data)




    