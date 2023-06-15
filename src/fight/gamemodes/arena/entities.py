import uuid

import pygame
import pygame.key
from pygame import Rect
from typing import TYPE_CHECKING, Dict, Union, List, Type, Tuple

from engine.entity import Entity
from engine.unresolved import Unresolved
from engine.physics_entity import PhysicsEntity
from engine.vector import Vector
from engine.events import LogicTick
from fight.gamemodes.arena.events import JumpEvent

if TYPE_CHECKING:
    from fight.gamemodes.arena.client import ArenaClient
    from fight.gamemodes.arena.server import ArenaServer
    from engine.gamemode_client import GamemodeClient
    from engine.gamemode_server import GamemodeServer 


class Cursor(Entity):
    def __init__(
        self, 
        game: Union["ArenaClient", "ArenaServer"], 
        updater: str, 
        rect=Rect(0,0,10,10), 
        id: str = None,
        sprite_path: str = None, 
        scale_res: tuple = None, 
        visible: bool = True
    ):

        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, id=id, scale_res=scale_res,
                         visible=visible)

        self.game.event_subscriptions[LogicTick].append(self.update_position)
    
    def draw(self):

        pygame.draw.rect(
            self.game.screen,
            (255,255,255),
            self.rect
        )

    def update_position(self, event: LogicTick):

        self.rect.center = pygame.mouse.get_pos()

class Floor(Entity):
    def __init__(
        self, 
        rect: Rect, 
        game: Union["ArenaClient", "ArenaServer"], 
        updater: str, 
        id: str = None,
        sprite_path: str = None, 
        scale_res: tuple = None, 
        visible: bool = True
    ):

        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, id=id, scale_res=scale_res,
                         visible=visible)

    def draw(self):
        # draw a white rectangle
        pygame.draw.rect(
            self.game.screen,
            (255,255,255),
            self.rect
        )

class Wall(Floor):
    # this exists for reasons trust me
    pass

class Player(PhysicsEntity):
    def __init__(
        self,
        rect: Rect, 
        game: Union["ArenaClient", "ArenaServer"], 
        updater: str, 
        health: int = 100, 
        weapon: Type["Weapon"] = None, 
        gravity=0.05, velocity = Vector(0,0), 
        max_velocity: Vector = Vector(50,50), 
        friction: int = 2, 
        collidable_entities: List[Type[Entity]] = [Floor, Wall, "self"], 
        id: str = None,
        sprite_path: str = None, 
        scale_res: tuple = None, 
        visible: bool = True
    ):

        super().__init__(gravity=gravity, velocity=velocity, max_velocity=max_velocity, friction=friction, collidable_entities=collidable_entities, rect=rect, game=game, updater=updater, sprite_path=sprite_path, id=id, scale_res=scale_res,
                         visible=visible)

        self.last_attack = 0

        self.health = health
        self.weapon = weapon

        self.game.event_subscriptions[LogicTick].append(self.handle_keys)
        

    def dict(self) -> Dict:

        data_dict = super().dict()

        data_dict["health"] = self.health

        if self.weapon is not None:
            data_dict["weapon"] = self.weapon.id
        else:
            data_dict["weapon"] = None
 

        return data_dict

    @classmethod
    def create(cls, entity_data: Dict[str, Union[int, bool, str, list]], entity_id: str, game: Union["ArenaClient", "ArenaServer"]):

        entity_data["health"] = entity_data["health"]

        if entity_data["weapon"] is not None:
            entity_data["weapon"] = Unresolved(entity_data["weapon"])
        else:
            entity_data["weapon"] = None

        new_player = super().create(entity_data, entity_id, game)

        return new_player

    def update(self, update_data: Dict):

        super().update(update_data)

        for attribute in update_data:

            match attribute:

                case "health":
                    self.health = update_data["health"]

                case "weapon":

                    if update_data["weapon"] is not None:
                        self.weapon = Unresolved(update_data["weapon"])
                    else:
                        self.weapon = None
    
    def draw(self):

        pygame.draw.rect(
            self.game.screen,
            (255,255,255),
            self.rect
        )

    def handle_keys(self, event: LogicTick):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:

            self.game.trigger(JumpEvent)
            
            if not self.airborne:
                self.velocity.y -= 10

        if keys[pygame.K_a]:
            self.velocity.x -= 1 

        if keys[pygame.K_d]:
            self.velocity.x += 1

class Weapon(Entity):
    def __init__(
        self, 
        ammo: int, 
        max_ammo: int, 
        attack_cooldown: int, 
        owner: Player, 
        rect: Rect, 
        game: Union["ArenaClient", "ArenaServer"], 
        updater: str, 
        id: str = None,
        sprite_path: str = None, 
        scale_res: Tuple[int, int] = None, 
        visible: bool = True
    ):

        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, id=id, scale_res=scale_res,
                         visible=visible)

        self.ammo = ammo
        self.max_ammo = max_ammo
        self.attack_cooldown = attack_cooldown
        self.owner = owner

        self.game.event_subscriptions[LogicTick] += [
            self.follow_owner,
            self.follow_cursor
        ]

    def dict(self) -> Dict:
        # create a json serializable dictionary with all of this object's attributes

        # create the base entity's dict, then we add our own unique attributes on top
        data_dict = super().dict()

        data_dict["ammo"] = self.ammo
        data_dict["max_ammo"] = self.max_ammo
        data_dict["attack_cooldown"] = self.attack_cooldown
        data_dict["owner"] = self.owner.id

        return data_dict

    @classmethod
    def create(
        cls, 
        entity_data: Dict[str, Union[int, bool, str, list]], 
        entity_id: str, 
        game: Union["ArenaClient", "ArenaServer"]
    ):
        # convert json entity data to object constructor arguments

        entity_data["ammo"] = entity_data["ammo"]
        entity_data["max_ammo"] = entity_data["max_ammo"]
        entity_data["attack_cooldown"] = entity_data["attack_cooldown"]
        entity_data["owner"] = Unresolved(entity_data["owner"])


        # call the base entity create method to do its own stuff and then return the actual object!!!!!
        new_player = super().create(entity_data, entity_id, game)

        return new_player

    def update(self, update_data: Dict):
        # update the attributes of this object with update data

        # update base entity attributes
        super().update(update_data)

        # loop through every attribute being updated
        for attribute in update_data:

            # we only need to check for attribute updates unique to this entity
            match attribute:

                case "ammo":
                    self.ammo = update_data["ammo"]
                
                case "max_ammo":
                    self.max_ammo = update_data["max_ammo"]

                case "attack_cooldown":
                    self.attack_cooldown = update_data["attack_cooldown"]

                case "owner":
                    self.owner = Unresolved(update_data["owner"])

    def follow_owner(self, event: LogicTick):
        self.rect = self.owner.rect.move(0,-50)

    def follow_cursor(self, event: LogicTick):
        mouse_pos = pygame.mouse.get_pos()

        #print(mouse_pos)

class Shotgun(Weapon):
    def __init__(
        self, 
        owner: Player, 
        rect: Rect, 
        game: Union["ArenaClient", "ArenaServer"], 
        updater: str, 
        ammo: int = 2, 
        max_ammo: int = 2, 
        attack_cooldown: int = 1, 
        id: str = None,
        sprite_path: str = "resources/shotgun.png", scale_res: Tuple[int, int] = (68,19), visible: bool = True
    ):

        super().__init__(ammo=ammo, max_ammo=max_ammo, attack_cooldown=attack_cooldown, owner=owner, rect=rect, game=game, updater=updater, sprite_path=sprite_path, id=id, scale_res=scale_res,
                         visible=visible)
        
class Portal(Entity):
    def __init__(
        self, 
        rect: Rect, 
        game: Union["GamemodeClient", "GamemodeServer"], 
        updater: str, 
        linked_portal: "Portal" = None, 
        id: str = None, 
        sprite_path: str = None, 
        scale_res: Tuple[int, int] = None, 
        visible: bool = True
    ):
    
        super().__init__(rect, game, updater, id, sprite_path, scale_res, visible)

        self.linked_portal = linked_portal
        self.last_tick_collisions = []

    def teleport_entities(self, event: LogicTick):

        colliding_entities = self.game.detect_collisions(self.rect)

        for entity in self.last_tick_collisions:
            # restore collisions with walls if entity left the portal
            if type(entity) is not PhysicsEntity:
                continue 

            if entity not in colliding_entities:
                print(f"entity {entity} left the portal")
                entity.collidable_entites.append(
                    Wall
                )

        for entity in colliding_entities:
            
            # allow physics entities to phase through walls if colliding with portal
            # we do this because portal entities are overlaid on top of walls
            if type(entity) is PhysicsEntity:
                entity.collidable_entites.remove(Wall)

            # check if the entity is colliding with the portal's hitbox and jutting out to the right
            # this indicates that the entity has entered all the way into the portal and should be teleported
            if entity.rect.right > self.rect.right:
                print(f"{entity} teleport!")
        
        self.last_tick_collisions = colliding_entities


