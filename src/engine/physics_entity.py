import uuid
from copy import copy
from typing import TYPE_CHECKING, Type, List, Union, Dict
from pygame import Rect

from engine.vector import Vector
from engine.entity import Entity
from engine.events import EntityLanded, LogicTick

if TYPE_CHECKING:
    from gamemode_client import GamemodeClient
    from gamemode_server import GamemodeServer

class PhysicsEntity(Entity):
    def __init__(
        self, 
        interaction_rect: Rect, 
        game: Union["GamemodeClient", "GamemodeServer"], 
        updater: str, 
        id: str, 
        gravity: int = 0, 
        velocity: Vector = Vector(0,0), 
        max_velocity: Vector = None, 
        friction=2, 
        collidable_entities: List[Type[Entity]] = [],
        airborne: bool = False
    ):

        super().__init__(interaction_rect=interaction_rect, game=game, updater=updater, id=id)
        
        self.velocity = velocity
        self.gravity = gravity
        self.max_velocity = max_velocity
        self.friction = friction
        self.collidable_entities = collidable_entities
        self.airborne = airborne

        # classes cannot reference themselves in their constructor arguments, so we just resolve "self" to the class of the entity
        if "self" in self.collidable_entities:
            self.collidable_entities.append(self.__class__)
        
            self.collidable_entities.remove("self")

        self.game.event_subscriptions[LogicTick] += [
            self.move_x_axis,
            self.move_y_axis,
            self.apply_friction,
            self.round_velocity,
            self.apply_gravity
        ]

        self.game.event_subscriptions[EntityLanded] += [
            self.bounce
        ]
    
    def serialize(self):

        data_dict = super().serialize()

        collidable_entity_type_strings = []
        
        for collidable_entity_type in self.collidable_entities:

            collidable_entity_type_strings.append(
                self.game.lookup_entity_type_string(collidable_entity_type)
            )

        print(collidable_entity_type_strings)

        #input(collidable_entity_type_strings)
        
        data_dict.update(
            {
                "velocity": [self.velocity.x, self.velocity.y],
                "gravity": self.gravity,
                "friction": self.friction,
                "collidable_entities": collidable_entity_type_strings,
                "airborne": self.airborne
            }
        )

        return data_dict
    
    @classmethod
    def create(cls, entity_data: Dict[str, Union[int, bool, str, list]], entity_id: str, game: Union["GamemodeClient", "GamemodeServer"]):
        # convert json entity data to object constructor arguments

        entity_data["velocity"] = Vector(
            entity_data["velocity"][0],
            entity_data["velocity"][1]
        )

        entity_data["gravity"] = entity_data["gravity"]

        entity_data["friction"] = entity_data["friction"]

        entity_data["airborne"] = entity_data["airborne"]

        #input(entity_data["collidable_entities"])

        for collidable_entity_type_string in entity_data["collidable_entities"].copy():

            # replace collidable entity type strings with the actual classes
            #input(collidable_entity_type_string)
            entity_data["collidable_entities"].append(
                game.entity_type_map[collidable_entity_type_string]
            )

            entity_data["collidable_entities"].remove(collidable_entity_type_string)

        # call the base entity create method to do its own stuff and then return the actual object!!!!!
        new_player = super().create(entity_data, entity_id, game)

        return new_player
    
    def update(self, update_data: Dict):

        super().update(update_data)

        # loop through every attribute being updated
        for attribute in update_data:

            match attribute:

                case "airborne":
                    self.airborne = update_data["airborne"]

                case "velocity":
                    self.velocity = Vector(
                        update_data["velocity"][0],
                        update_data["velocity"][1]
                    )

                case "gravity":
                    
                    self.gravity = update_data["gravity"]
                    
                case "friction":
                    
                    self.friction = update_data["friction"]

                case "collidable_entities":

                    collidable_entities = []

                    for collidable_entity_type_string in update_data["collidable_entities"]:

                        # replace collidable entity type strings with the actual classes

                        collidable_entities.append(
                            self.game.entity_type_map[collidable_entity_type_string]
                        )

                    self.collidable_entities = collidable_entities

    def move_x_axis(self, event: LogicTick):
        """Move entity by velocity but stop if colliding into collidable entity"""

        # enforce max velocity
        if abs(self.velocity.x) > abs(self.max_velocity.x):
            self.velocity.x = self.max_velocity.x * self.velocity.normalize().x

        projected_rect_x = self.interaction_rect.move(
            Vector(self.velocity.x, 0)
        )

        colliding_entities = self.game.detect_collisions(projected_rect_x)

        if self in colliding_entities:
            del colliding_entities[colliding_entities.index(self)]

        # remove any entities that we shouldnt collide with
        for colliding_entity in copy(colliding_entities):

            if type(colliding_entity) not in self.collidable_entities:
                del colliding_entities[colliding_entities.index(colliding_entity)]

        if len(colliding_entities) != 0:

            colliding_entity = colliding_entities[0]

            # entity came in moving left
            if projected_rect_x.right >= colliding_entity.interaction_rect.left and self.interaction_rect.right < colliding_entity.interaction_rect.left:
                self.interaction_rect.right = colliding_entity.interaction_rect.left
            
            # entity came in moving right
            elif projected_rect_x.left <= colliding_entity.interaction_rect.right and self.interaction_rect.left > colliding_entity.interaction_rect.right:
                self.interaction_rect.left = colliding_entity.interaction_rect.right
        
        else:

            self.interaction_rect.x = projected_rect_x.x

    def move_y_axis(self, event: LogicTick):
        
        # enforce max velocity
        if abs(self.velocity.y) > abs(self.max_velocity.y):
            self.velocity.y = self.max_velocity.y * self.velocity.normalize().y
        
        projected_rect_y = self.interaction_rect.move(
            Vector(0, self.velocity.y)
        )

        colliding_entities = self.game.detect_collisions(projected_rect_y)

        if self in colliding_entities:
            del colliding_entities[colliding_entities.index(self)]

        # remove any entities that we shouldnt collide with
        for colliding_entity in copy(colliding_entities):

            if type(colliding_entity) not in self.collidable_entities:
                del colliding_entities[colliding_entities.index(colliding_entity)]

        if len(colliding_entities) != 0:
            
            # only calculate collision for the first entity in list
            # this may cause issues later when lots of entities are colliding at once
            colliding_entity = colliding_entities[0]

            colliding_entity: Type[Entity]

            # new rect bottom is lower than the colliding rect's top and the old rect bottom is higher than the colliding rect top
            if (projected_rect_y.bottom >= colliding_entity.interaction_rect.top) and (self.interaction_rect.bottom <= colliding_entity.interaction_rect.top):

                self.interaction_rect.bottom = colliding_entity.interaction_rect.top

                self.velocity.y = 0

                self.airborne = False

                self.game.trigger(EntityLanded(self))

            # entity came in moving up
            elif projected_rect_y.top <= colliding_entity.interaction_rect.bottom and self.interaction_rect.top >= colliding_entity.interaction_rect.bottom:

                self.interaction_rect.top = colliding_entity.interaction_rect.bottom
                
        else:
            self.interaction_rect.y = projected_rect_y.y

            self.airborne = True

    def apply_friction(self, event: LogicTick):
        
        print(self.velocity.x)
        if abs(self.velocity.x) > 0:
            
            self.velocity.x *= 0.9
            

    def apply_gravity(self, event: LogicTick):

        self.velocity.y += self.gravity

    def bounce(self, event: EntityLanded):

        if event.entity.id != self.id:
            print
            return

        
        self.velocity.y *= -0.25
    
    def round_velocity(self, event: LogicTick):
        self.velocity.x = round(self.velocity.x, 4)
        self.velocity.y = round(self.velocity.y, 4)
