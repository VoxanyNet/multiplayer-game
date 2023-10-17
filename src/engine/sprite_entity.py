from abc import abstractproperty
from typing import Dict, Optional

from pygame import Surface

from engine.drawable_entity import DrawableEntity
from engine.entity import Entity
from engine.gamemode_client import GamemodeClient
from engine.gamemode_server import GamemodeServer

class MissingSpritePath(Exception):
    pass 

class SpriteEntity(DrawableEntity):

    def __init__(self, game: GamemodeClient | GamemodeServer, updater: str, draw_layer: int, active_sprite: Optional[Surface], id: str | None = None):

        DrawableEntity.__init__(
            self=self,
            game=game, 
            updater=updater, 
            draw_layer=draw_layer, 
            id=id
        )

        self.active_sprite = active_sprite
    
    def serialize(self) -> Dict[str, int | bool | str | list]:

        data_dict = DrawableEntity.serialize(self)

        active_sprite_path = None

        if self.active_sprite:
            
            for path, sprite in self.game.resources.items():
                if self.active_sprite == sprite:
                    active_sprite_path = path

            if active_sprite_path is None:
                raise MissingSpritePath(f"cannot find path for active sprite {sprite}")
        
        data_dict.update(
            {
                "active_sprite": active_sprite_path
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

    @staticmethod
    def deserialize(entity_data: Dict[str, int | bool | str | list], entity_id: str, game: type[GamemodeClient] | type[GamemodeServer]) -> dict:
        
        if entity_data["active_sprite"] is None:
            entity_data["active_sprite"] = None
        else:
            entity_data["active_sprite"] = game.resources[entity_data["active_sprite"]]
        
        entity_data.update(DrawableEntity.deserialize(entity_data, entity_id, game))

        return entity_data

    def draw_onto_body(self):
        """Draw sprite onto pymunk body if the entity has one"""
        if not hasattr(self, "body"):
            raise Exception("SpriteEntity.draw_onto_body not supported when entity has no body")
        
        
        
