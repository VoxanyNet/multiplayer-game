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
            game: Union["GamemodeClient", "GamemodeServer"], 
            updater: str, 
            id: str
        ):

        super().__init__(game=game, updater=updater, id=id)

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
                    "position": (round(self.body.position.x, 3), round(self.body.position.y, 3)),
                    "mass": self.body.mass,
                    "moment": self.body.moment
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
        
        body = pymunk.Body(
            mass=entity_data["body"]["mass"],
            moment=entity_data["body"]["moment"],
            body_type=pymunk.Body.STATIC # if we dont own the tile, we dont want to simulate its position
        )

        body.position = entity_data["body"]["position"]

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
        
        print(update_data)

        for attribute_name, attribute_value in update_data.items():

            match attribute_name:
                
                case "body":
                    
                    for sub_attribute_name, sub_attribute_value in attribute_value.items():

                        match sub_attribute_name:

                            case "angle":
                                self.body.angle = update_data["body"]["angle"]
                            
                            case "position":
                                self.body.position = update_data["body"]["position"]
                            
                            case "mass":
                                self.body.mass = update_data["body"]["mass"]

                            case "moment":
                                self.body.moment = update_data["body"]["moment"]

                case "shape":

                    for sub_attribute_name, sub_attribute_value in attribute_value.items():

                        match sub_attribute_name:

                            case "vertices": # i will save this for a later date
                                # remove old shape from body
                                # make new shape with updated vertices
                                pass

                            case "friction":
                                self.shape.friction = update_data["shape"]["friction"]





    