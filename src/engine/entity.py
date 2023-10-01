import uuid
import inspect
from typing import Dict, List, Type, Tuple, Union, TYPE_CHECKING, get_type_hints, Callable, Optional
import json

import pygame.image
from pygame import Rect
from rich import print

from engine.unresolved import Unresolved
from engine.helpers import get_matching_objects, dict_diff
from engine.events import TickComplete, NetworkTick, NewEntity

if TYPE_CHECKING:
    from gamemode_client import GamemodeClient
    from gamemode_server import GamemodeServer

class MissingSpritePath(Exception):
    pass 

class Entity:
    
    def __init__(
        self, 
        game: Union["GamemodeClient", "GamemodeServer"], 
        updater: str, 
        id: Optional[str]=None, 
        active_sprite: Optional[pygame.Surface]=None,
        draw_layer: Optional[int] = None
    ):

        self.updater = updater
        self.game = game
        self.last_tick_dict = {}
        self.draw_layer: Optional[int] = draw_layer
        
        if id is None:
            id = str(uuid.uuid4())[0:6]
        
        self.id = id

        self.active_sprite: Optional[pygame.Surface] = active_sprite

        # add entity to the game state automatically
        self.game.entities[self.id] = self

        self.game.event_subscriptions[NetworkTick] += [self.detect_updates] 

        self.game.trigger(NewEntity(new_entity=self))

    def kill(self):
        """Remove entity from entity list and remove all event listeners""" 

        # this is kind of a band aid fix, not sure how this should be done
        if self.updater is self.game.uuid:
            self.game.network_update(update_type="delete", entity_id=self.id)
        
        del self.game.entities[self.id]

        for event, event_listeners in self.game.event_subscriptions.items():
            for listener in event_listeners.copy():          
                if listener.__self__ is self:
                    event_listeners.remove(listener)


    def detect_updates(self, event: NetworkTick):
        """Compare entity state from last tick to this tick to find differences"""

        current_tick_dict = self.serialize()
        
        # this indicates that the entity did not exist last tick
        if self.last_tick_dict == {}:
            self.game.network_update(
                update_type="create",
                entity_id=self.id,
                data=current_tick_dict,
                entity_type_string=self.game.lookup_entity_type_string(self)
            )
        
        # if not a new entity, check for changes
        elif current_tick_dict != self.last_tick_dict:
            
            update_data_dict = dict_diff(self.last_tick_dict, current_tick_dict)

            #print(update_data_dict)

            self.game.network_update(update_type="update", entity_id=self.id, data=update_data_dict)

            #print(json.dumps(update_data_dict))
        
        self.last_tick_dict = current_tick_dict
                
    def resolve(self):
        """Convert any of the entity's attributes that are of type 'Unresolved' to the actual entity they are pointing to"""

        for attribute_name, attribute in self.__dict__.copy().items():

            if type(attribute) is not Unresolved:
                continue

            resolved_attribute = self.game.entities[
                attribute.uuid
            ]

            self.__setattr__(attribute_name, resolved_attribute)

    def serialize(self) -> Dict[str, Union[int, bool, str, list]]:
        """Serialize the entity's data"""
        
        active_sprite_path = None
        
        # find path for active sprite
        if self.active_sprite:

            for path, sprite in self.game.resources.items():
                if self.active_sprite == sprite:
                    active_sprite_path = path

            if active_sprite_path is None:
                raise MissingSpritePath(f"cannot find path for active sprite {sprite}")
            
        data_dict = {
            "updater": self.updater,
            "active_sprite": active_sprite_path,
            "draw_layer": self.draw_layer
        }
        
        return data_dict

    @classmethod
    def create(cls, entity_data: Dict[str, Union[int, bool, str, list]], entity_id: str, game: Union[Type["GamemodeClient"], Type["GamemodeServer"]]) -> Type["Entity"]:
        """Use serialized entity data to create a new entity"""

        entity_data["updater"] = entity_data["updater"]
        entity_data["draw_layer"] = entity_data["draw_layer"]        
        
        if entity_data["active_sprite"] is not None: # this is verbose but clearer
            entity_data["active_sprite"] = game.resources[entity_data["active_sprite"]]

        return cls(game=game, id=entity_id, **entity_data)

    def update(self, update_data):
        """Use serialized entity data to update existing entity"""

        for attribute in update_data:

            match attribute:

                case "updater":
                    self.updater = update_data["updater"]

                case "active_sprite":
                    if update_data["active_sprite"] is not None:
                        self.active_sprite = self.game.resources[update_data["active_sprite"]]
                    else:
                        self.active_sprite = None
                
                case "draw_layer":
                    self.draw_layer = update_data["draw_layer"]