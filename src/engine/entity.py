import uuid
from typing import Dict, List, Type, Union, TYPE_CHECKING

import pygame.image
from pygame import Rect

from engine.unresolved import Unresolved
from engine.helpers import get_matching_objects, dict_diff
from engine.events import LogicTick, GameTickComplete, GameTickStart, EntityCreated

if TYPE_CHECKING:
    from gamemode_client import GamemodeClient
    from gamemode_server import GamemodeServer


class Entity:
    def __init__(self, rect: Rect, game: Union["GamemodeClient", "GamemodeServer"], updater: str, uuid=str(uuid.uuid4()), sprite_path=None, scale_res=None,
                 visible=True):

        self.visible = visible
        self.rect = rect
        self.updater = updater
        self.uuid = uuid
        self.game = game
        self.sprite_path = sprite_path
        self.scale_res = scale_res
        self.last_tick_dict = {}

        self.game.entities[self.uuid] = self

        if sprite_path:
            self.sprite = pygame.image.load(sprite_path)

        if scale_res and sprite_path:
            print("scaling")
            self.sprite = pygame.transform.scale(self.sprite, scale_res)

        #self.game.event_subscriptions[GameTickStart] += [self.set_last_tick_dict]
        self.game.event_subscriptions[GameTickComplete] += [self.detect_updates] 

    def set_last_tick_dict(self, event: GameTickStart):
        """Set a keyframe of the serialized object before it ticked"""

        self.last_tick_dict = self.dict()

    def detect_updates(self, event: GameTickComplete):
        """Compare entity state from last tick to this tick to find differences"""

        current_tick_dict = self.dict()
        
        # this indicates that the entity did not exist last tick
        if self.last_tick_dict == {}:
            self.game.network_update(
                update_type="create",
                entity_id=self.uuid,
                data=self.dict(),
                entity_type_string=self.game.lookup_entity_type_string(self)
            )

            print(f"Sending create update for {self.uuid}")

            self.last_tick_dict = current_tick_dict

            return

        if current_tick_dict != self.last_tick_dict:
            
            update_data_dict = dict_diff(self.last_tick_dict, current_tick_dict)

            print(update_data_dict)

            self.game.network_update(update_type="update", entity_id=self.uuid, data=update_data_dict)
        
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

    def dict(self) -> Dict[str, Union[int, bool, str, list]]:
        """Serialize the entity's data"""

        data_dict = {
            "rect": list(self.rect),
            "visible": self.visible,
            "updater": self.updater,
            "sprite_path": self.sprite_path,
            "scale_res": self.scale_res
        }

        return data_dict

    @classmethod
    def create(cls, entity_data: Dict[str, Union[int, bool, str, list]], entity_id: str, game: Union[Type["GamemodeClient"], Type["GamemodeServer"]]) -> Type["Entity"]:
        """Use serialized entity data to create a new entity"""

        entity_data["rect"] = Rect(
            entity_data["rect"]
        )

        entity_data["visible"] = entity_data["visible"]

        entity_data["updater"] = entity_data["updater"]

        entity_data["sprite_path"] = entity_data["sprite_path"]

        entity_data["scale_res"] = entity_data["scale_res"]

        return cls(game=game, uuid=entity_id, **entity_data)

    def update(self, update_data):
        """Use serialized entity data to update existing entity"""

        for attribute in update_data:

            match attribute:

                case "visible":
                    self.visible = update_data["visible"]

                case "rect":
                    
                    self.rect.update(
                        update_data["rect"]
                    )

                case "updater":
                    self.updater = update_data["updater"]

                case "sprite_path":
                    self.sprite = pygame.image.load(update_data["sprite_path"])
        
    def draw(self):
        """Draw the entity onto the game screen"""

        self.game.screen.blit(self.sprite, self.rect)
