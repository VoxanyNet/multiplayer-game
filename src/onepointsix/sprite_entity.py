from abc import abstractproperty
import time
from typing import Dict, Optional, List
import math 

from pygame import Surface
import pygame

from onepointsix.drawable_entity import DrawableEntity
from onepointsix.entity import Entity
from onepointsix.gamemode_client import GamemodeClient
from onepointsix.gamemode_server import GamemodeServer

class MissingSpritePath(Exception):
    pass 

class SpriteEntity(DrawableEntity):

    def __init__(
        self, 
        game: GamemodeClient | GamemodeServer, 
        updater: str, 
        draw_layer: int, 
        active_sprite: Optional[Surface] = None, 
        id: str | None = None,
        scale: int = 1,
        *args,
        **kwargs
    ):

        super().__init__(
            game, 
            updater, 
            draw_layer, 
            id,
            *args,
            **kwargs
        )

        self.active_sprite = active_sprite
        self.scale = scale
    
    def serialize(self) -> Dict[str, int | bool | str | list | None]:

        data_dict = DrawableEntity.serialize(self)

        path: Optional[str] = None 
        sprite: Optional[pygame.Surface] = None 
        active_sprite_path: Optional[str] = None

        if self.active_sprite:
            for path, sprite in self.game.resources.items():
                if self.active_sprite == sprite:
                    active_sprite_path = path

            if active_sprite_path is None:
                raise MissingSpritePath(f"cannot find path for active sprite {sprite}")
        
        data_dict.update(
            {
                "active_sprite": active_sprite_path,
                "scale": self.scale
            }
        )
        
        return data_dict
    
    def update(self, update_data: dict):
        DrawableEntity.update(self, update_data)

        for attribute_name, attribute_value in update_data.items():
            match attribute_name:
                case "active_sprite":

                    if attribute_value is None:
                        self.active_sprite = None
                    
                    else:
                        self.active_sprite = self.game.resources[attribute_value]
                
                case "scale":
                    self.scale = attribute_value

    @staticmethod
    def deserialize(entity_data: dict, entity_id: str, game: GamemodeClient | GamemodeServer) -> dict:
        
        if entity_data["active_sprite"] is None:
            entity_data["active_sprite"] = None
        else:
            entity_data["active_sprite"] = game.resources[entity_data["active_sprite"]]
        
        entity_data["scale"] = entity_data["scale"]
        
        entity_data.update(DrawableEntity.deserialize(entity_data, entity_id, game))

        return entity_data

    def draw_onto_body(self):
        """Draw sprite onto pymunk body if the entity has one"""
        if not hasattr(self, "body"):
            raise Exception("SpriteEntity.draw_onto_body only supported when entity has body")
        
        active_sprite_scaled = pygame.transform.scale_by(
            self.active_sprite,
            self.scale
        )

        active_sprite_rotated = pygame.transform.rotate(
            active_sprite_scaled,
            math.degrees(self.body.angle) * -1
        )

        self.game.screen.blit(
            active_sprite_rotated,
            (
                self.shape.bb.left + self.game.camera_offset[0],
                self.shape.bb.bottom + self.game.camera_offset[1]
            )
        )
        
        
        
