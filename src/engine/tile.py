from typing import Dict, Tuple, Union, Type, TYPE_CHECKING, Optional
import gc

import pymunk
from pygame import Rect
import pygame
from rich import print

from engine.entity import Entity
from engine.unresolved import Unresolved
from engine.events import Tick

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
            id: Optional[str] = None
        ):

        super().__init__(game=game, updater=updater, id=id)

        self.game.event_subscriptions[Tick] += [
            self.despawn
        ]

        self.body = body 
        self.shape = shape

        self.game.space.add(self.body, self.shape)

        print(self.body.center_of_gravity)
    
    def kill(self):

        super().kill()

        self.game.space.remove(self.body, self.shape)
    
    def despawn(self, event: Tick):
        # FIX ME!!!
        return
        max_x = self.game.boundry_rect.right - self.game.boundry_rect.left
        max_y = self.game.boundry_rect.get_height()

        if self.body.position.x > max_x or self.body.position.y > max_y:
            self.kill()



        

        
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

    
    def serialize(self) -> Dict[str, int | bool | str | list]:

        data_dict = super().serialize()

        if self.body.body_type is pymunk.Body.DYNAMIC:
            body_type_string = "dynamic"
        elif self.body.body_type is pymunk.Body.STATIC:
            body_type_string = "static"
        elif self.body.body_type is pymunk.Body.KINEMATIC:
            body_type_string = "kinematic"

        data_dict.update(
            {   
                "body": {
                    "angle": round(self.body.angle, 4),
                    "position": (round(self.body.position.x, 4), round(self.body.position.y, 4)),
                    #"mass": self.body.mass,
                    "moment": self.body.moment,
                    "type": "kinematic",
                    "velocity": (round(self.body.velocity.x, 6), round(self.body.velocity.y, 6))
                },
                "shape": {
                    "vertices": self.shape.get_vertices(),
                    "friction": self.shape.friction,
                    "elasticity": self.shape.elasticity
                }
            }    
        )
            
        #print(data_dict)

        return data_dict
    
    @classmethod
    def create(self, entity_data: Dict[str, Union[int, bool, str, list]], entity_id: str, game: Union["GamemodeClient", "GamemodeServer"]) -> Type["Tile"]:
        """Translate serialized entity data into an actual Tile object"""

        match entity_data["body"]["type"]:

            case "dynamic":
                body_type = pymunk.Body.DYNAMIC
            
            case "static":
                body_type = pymunk.Body.STATIC

            case "kinematic":
                body_type = pymunk.Body.KINEMATIC
        
        body = pymunk.Body(
            #mass=entity_data["body"]["mass"],
            moment=entity_data["body"]["moment"],
            body_type=body_type
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
        

        return super().create(entity_data, entity_id, game=game)

    def update(self, update_data: dict):

        super().update(update_data)
        
        for attribute_name, attribute_value in update_data.items():

            match attribute_name:
                
                case "body":
                    
                    for sub_attribute_name, sub_attribute_value in attribute_value.items():

                        match sub_attribute_name:

                            case "velocity":
                                self.body.velocity = update_data["body"]["velocity"]

                            case "angle":
                                self.body.angle = update_data["body"]["angle"]
                            
                            case "position":
                                self.body.position = update_data["body"]["position"]
                            
                            case "mass":
                                if self.body.body_type is pymunk.Body.STATIC:
                                    continue
                                
                                self.body.mass = update_data["body"]["mass"]

                            case "moment":
                                self.body.moment = update_data["body"]["moment"]
                            
                            case "type":

                                match update_data["body"]["type"]:

                                    case "dynamic":
                                        body_type = pymunk.Body.DYNAMIC
                                    
                                    case "static":
                                        body_type = pymunk.Body.STATIC

                                    case "kinematic":
                                        body_type = pymunk.Body.KINEMATIC

                                self.body.body_type = body_type

                case "shape":

                    for sub_attribute_name, sub_attribute_value in attribute_value.items():

                        match sub_attribute_name:

                            case "vertices": # i will save this for a later date
                                # remove old shape from body
                                # make new shape with updated vertices
                                pass

                            case "friction":
                                self.shape.friction = update_data["shape"]["friction"]
                            
                            case "elasticity":
                                self.shape.elasticity = update_data["shape"]["elasticity"]





    