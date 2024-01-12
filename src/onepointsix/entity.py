import uuid
import inspect
from typing import Dict, List, Type, Tuple, Union, TYPE_CHECKING, get_type_hints, Callable, Optional
import json
from abc import ABC

import pygame.image
from pygame import Rect
from rich import print

from onepointsix.unresolved import Unresolved
from onepointsix.helpers import get_matching_objects, dict_diff
from onepointsix.events import TickComplete, NetworkTick, NewEntity

if TYPE_CHECKING:
    from gamemode_client import GamemodeClient
    from gamemode_server import GamemodeServer
    
class Entity(ABC):
    
    def __init__(
        self,
        game: Union["GamemodeClient", "GamemodeServer"], 
        updater: str, 
        id: Optional[str]=None,
        *args,
        **kwargs
    ):

        self.updater = updater
        self.game = game
        self.update_checkpoint = {}

        if id is None:
            id = str(uuid.uuid4())[0:6]
        
        self.id = id

        # add entity to the game state automatically
        self.game.entities[self.id] = self

        self.game.trigger(NewEntity(new_entity=self))

    def kill(self):
        """Remove entity from entity list and remove all event listeners""" 

        # this is kind of a band aid fix, not sure how this should be done
        if self.updater is self.game.uuid:
            self.game.network_update(update_type="delete", entity_id=self.id)
            
            # delete any outgoing updates that reference this entity
            # for update in self.game.outgoing_updates_queue.copy():

            #     update_index = self.game.outgoing_updates_queue.index(update)

            #     if update["entity_id"] == self.id:
            #         del self.game.outgoing_updates_queue[update_index]
            #         print(f"deleted {update}")
        
        print(f"deleting {self.id} {self.game.tick_count}")
        del self.game.entities[self.id]

        for event, event_listeners in self.game.event_subscriptions.items():
            for listener in event_listeners.copy():          
                if listener.__self__ is self:
                    event_listeners.remove(listener)

    def set_update_checkpoint(self):
        self.update_checkpoint = self.serialize()

    def detect_updates(self):
        """Compare entity state from last tick to this tick to find differences"""

        current_tick_dict = self.serialize()
        
        # this indicates that the entity did not exist last tick
        if self.update_checkpoint == {}:
            self.game.network_update(
                update_type="create",
                entity_id=self.id,
                data=current_tick_dict,
                entity_type_string=self.game.lookup_entity_type_string(self)
            )
        
        # if not a new entity, check for changes
        elif current_tick_dict != self.update_checkpoint:
            
            update_data_dict = dict_diff(self.update_checkpoint, current_tick_dict)

            #print(update_data_dict)

            self.game.network_update(update_type="update", entity_id=self.id, data=update_data_dict)

            #print(json.dumps(update_data_dict))
                
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
            
        data_dict = {
            "updater": self.updater
        }
        
        return data_dict

    @staticmethod
    def deserialize(entity_data: Dict[str, Union[int, bool, str, list]], entity_id: str, game: Union[Type["GamemodeClient"], Type["GamemodeServer"]]):
        """Deserialize a dictionary of entity init arguments into proper objects"""

        entity_data["updater"] = entity_data["updater"]    

        return entity_data

    def update(self, update_data):
        """Use serialized entity data to update existing entity"""

        for attribute in update_data:

            match attribute:

                case "updater":
                    self.updater = update_data["updater"]