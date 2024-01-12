from typing import Dict, Tuple, Union, Type, TYPE_CHECKING, Optional
import gc

import pymunk
from pygame import Rect
import pygame
from rich import print

from onepointsix.entity import Entity
from onepointsix.unresolved import Unresolved
from onepointsix.events import Tick
from onepointsix.drawable_entity import DrawableEntity

if TYPE_CHECKING:
    from onepointsix.gamemode_client import GamemodeClient
    from onepointsix.gamemode_server import GamemodeServer

class Tile(Entity):
    def __init__(
            self, 
            body: pymunk.Body,
            shape: pymunk.Shape,
            game: Union["GamemodeClient", "GamemodeServer"], 
            updater: str, 
            id: Optional[str] = None,
            *args,
            **kwargs
        ):

        super().__init__(
            game=game, 
            updater=updater, 
            id=id,
            *args,
            **kwargs
        )

        self.game.event_subscriptions[Tick] += [
            #self.despawn
        ]

        self.body = body 
        self.shape = shape
        self.color = (255,255,255)

        self.game.space.add(self.body, self.shape)
        
    def kill(self):
  
        Entity.kill(self)

        self.game.space.remove(self.body, self.shape)
    
    def despawn(self, event: Tick):

        max_x = self.game.boundry_rect.right - self.game.boundry_rect.left
        max_y = self.game.boundry_rect.bottom - self.game.boundry_rect.top

        if self.body.position.x > max_x or self.body.position.y > max_y:
            self.kill()

    def debug_draw(self):

        vertices = []

        for vertex in self.shape.get_vertices():
            # vertices are not relative to the world, so we need to add the body position
            x = vertex.rotated(self.shape.body.angle)[0] + self.shape.body.position[0]
            y = vertex.rotated(self.shape.body.angle)[1] + self.shape.body.position[1]

            x += self.game.camera_offset[0]
            y += self.game.camera_offset[1]

            vertices.append((x, y))

        pygame.draw.polygon(
            self.game.screen,
            self.color,
            vertices
        )

    
    def serialize(self) -> Dict[str, int | bool | str | list]:

        data_dict = Entity.serialize(self)

        data_dict.update(
            {   
                "body": {
                    "angle": round(self.body.angle, 1),
                    "position": (round(self.body.position.x, 2), round(self.body.position.y, 2)),
                    "moment": self.body.moment,
                    "velocity": (round(self.body.velocity.x, 0), round(self.body.velocity.y, 0))
                },
                "shape": {
                    "vertices": self.shape.get_vertices(),
                    "friction": self.shape.friction,
                    "elasticity": self.shape.elasticity
                }
            }    
        )

        return data_dict
    
    @staticmethod
    def deserialize(entity_data: Dict[str, Union[int, bool, str, list]], entity_id: str, game: Union["GamemodeClient", "GamemodeServer"]) -> dict:
        """Translate serialized entity data into an actual Tile object"""
        
        body = pymunk.Body(
            moment=entity_data["body"]["moment"],
            body_type=pymunk.Body.DYNAMIC
        )

        body.position = entity_data["body"]["position"]
        body.angle = entity_data["body"]["angle"]
        body.velocity = entity_data["body"]["velocity"]

        entity_data["body"] = body

        shape = pymunk.Poly(
            body=body,
            vertices=entity_data["shape"]["vertices"]
        )
        shape.friction = entity_data["shape"]["friction"]
        shape.elasticity = entity_data["shape"]["elasticity"]

        entity_data["shape"] = shape
        
        entity_data.update(Entity.deserialize(entity_data, entity_id, game=game))

        return entity_data
        

    def update(self, update_data: dict):

        Entity.update(self, update_data)
        
        for attribute_name, attribute_value in update_data.items():

            match attribute_name:
                
                case "body":
                    
                    for sub_attribute_name, sub_attribute_value in attribute_value.items():
                        
                        # we dont want to receive position updates from other clients
                        if self.updater is not self.game.uuid:

                            match sub_attribute_name:
                                
                                case "velocity":
                                    self.body.velocity = sub_attribute_value

                                case "angle":
                                    self.body.angle = sub_attribute_value 
                                
                                case "position":
                                    self.body.position = sub_attribute_value

                case "shape":

                    for sub_attribute_name, sub_attribute_value in attribute_value.items():

                        match sub_attribute_name:

                            case "vertices": # i will save this for a later date
                                # remove old shape from body
                                # make new shape with updated vertices
                                pass

                            case "friction":
                                self.shape.friction = sub_attribute_value
                            
                            case "elasticity":
                                self.shape.elasticity = sub_attribute_value





    