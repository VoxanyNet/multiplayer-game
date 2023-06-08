import uuid
from copy import copy
from typing import TYPE_CHECKING, Type, List, Union, Dict
from pygame import Rect

from engine.vector import Vector
from engine.entity import Entity
from engine.events import EntityLanded, EntityAirborne, LogicTick

if TYPE_CHECKING:
    from gamemode_client import GamemodeClient
    from gamemode_server import GamemodeServer

class PhysicsEntity(Entity):
    def __init__(self, rect: Rect, game: Union["GamemodeClient", "GamemodeServer"], updater: str, uuid=str(uuid.uuid4()), gravity: int = 0, velocity: Vector = Vector(0,0), max_velocity=None, friction=2, collidable_entities: List[Type[Entity]] = [], sprite_path: str = None, scale_res: tuple = None, visible: bool = True):

        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res, visible=visible)
        
        self.velocity = velocity
        self.gravity = gravity
        self.max_velocity = max_velocity
        self.friction = friction
        self.collidable_entites = collidable_entities

        # classes cannot reference themselves in their constructor arguments, so we just resolve "self" to the class of the entity
        if "self" in self.collidable_entites:
            self.collidable_entites.append(self.__class__)
        
        self.collidable_entites.remove("self")

        self.game.event_subscriptions[LogicTick] += [
            self.move_x_axis,
            self.move_y_axis,
            self.apply_friction
        ]

        self.game.event_subscriptions[EntityLanded] += [
            self.bounce
        ]

        self.game.event_subscriptions[EntityAirborne] += [
            self.apply_gravity
        ]
    
    def dict(self):

        data_dict = super().dict()
        
        data_dict.update(
            {
                "velocity": [self.velocity.x, self.velocity.y],
                "gravity": self.gravity,
                "friction": self.friction
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

        # call the base entity create method to do its own stuff and then return the actual object!!!!!
        new_player = super().create(entity_data, entity_id, game)

        return new_player
    
    def update(self, update_data: Dict):

        super().update(update_data)

        # loop through every attribute being updated
        for attribute in update_data:

            match attribute:

                case "velocity":
                    self.velocity = Vector(
                        update_data["velocity"][0],
                        update_data["velocity"][1]
                    )

                case "gravity":
                    
                    self.gravity = update_data["gravity"]
                    
                case "friction":
                    
                    self.friction = update_data["friction"]

    def move_x_axis(self, event: LogicTick):
        """Move entity by velocity but stop if colliding into collidable entity"""

        projected_rect_x = self.rect.move(
            Vector(self.velocity.x, 0)
        )

        colliding_entities = self.game.detect_collisions(projected_rect_x)

        if self in colliding_entities:
            del colliding_entities[colliding_entities.index(self)]

        # remove any entities that we shouldnt collide with
        for colliding_entity in copy(colliding_entities):

            if type(colliding_entity) not in self.collidable_entites:
                del colliding_entities[colliding_entities.index(colliding_entity)]

        if len(colliding_entities) != 0:

            colliding_entity = colliding_entities[0]

            # entity came in moving left
            if projected_rect_x.right >= colliding_entity.rect.left and self.rect.right < colliding_entity.rect.left:
                self.rect.right = colliding_entity.rect.left
            
            # entity came in moving right
            elif projected_rect_x.left <= colliding_entity.rect.right and self.rect.left > colliding_entity.rect.right:
                self.rect.left = colliding_entity.rect.right
        
        else:

            self.rect.x = projected_rect_x.x

    def move_y_axis(self, event: LogicTick):
        
        projected_rect_y = self.rect.move(
            Vector(0, self.velocity.y)
        )

        colliding_entities = self.game.detect_collisions(projected_rect_y)

        if self in colliding_entities:
            del colliding_entities[colliding_entities.index(self)]

        # remove any entities that we shouldnt collide with
        for colliding_entity in copy(colliding_entities):

            if type(colliding_entity) not in self.collidable_entites:
                del colliding_entities[colliding_entities.index(colliding_entity)]

        if len(colliding_entities) != 0:

            colliding_entity = colliding_entities[0]

            colliding_entity: Type[Entity]

            # new rect bottom is lower than the colliding rect's top and the old rect bottom is higher than the colliding rect top
            if (projected_rect_y.bottom >= colliding_entity.rect.top) and (self.rect.bottom <= colliding_entity.rect.top):

                self.rect.bottom = colliding_entity.rect.top

                self.velocity.y = 0

                self.game.trigger(EntityLanded(self))

            # entity came in moving up
            elif projected_rect_y.top <= colliding_entity.rect.bottom and self.rect.top >= colliding_entity.rect.bottom:
                self.rect.top = colliding_entity.rect.bottom
                
        else:
            self.rect.y = projected_rect_y.y

            self.game.trigger(EntityAirborne(entity=self))

    def apply_friction(self, event: LogicTick):

        if abs(self.velocity.x) > 0:

            self.velocity.x *= 0.05
            

    def apply_gravity(self, event: EntityAirborne):

        if event.entity is self:
            self.velocity.y += self.gravity

    def bounce(self, event: EntityLanded):

        if event.entity.uuid != self.uuid:
            print
            return

        
        self.velocity.y *= -0.25