import uuid

import pygame.key

from engine.entity import Entity

import uuid

import pygame
import pygame.key
from pygame import Rect

from engine.entity import Entity 
from engine.unresolved import Unresolved
from engine.physics_entity import PhysicsEntity
from engine.vector import Vector
from engine.events import TickEvent

class Floor(Entity):

    def __init__(self, rect=None, game=None, updater=None, uuid=str(uuid.uuid4()),
                 sprite_path=None, scale_res=None, visible=True):

        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

    def dict(self):
        # create a json serializable dictionary with all of this object's attributes

        # create the base entity's dict, then we add our own unique attributes on top
        data_dict = super().dict()

        return data_dict

    @classmethod
    def create(cls, entity_data, entity_id, game):
        # convert json entity data to object constructor arguments

        # call the base entity create method to do its own stuff and then return the actual object!!!!!
        new_player = super().create(entity_data, entity_id, game)

        return new_player

    def update(self, update_data):
        # update the attributes of this object with update data

        # update base entity attributes
        super().update(update_data)

        # loop through every attribute being updated
        for attribute in update_data:

            # we only need to check for attribute updates unique to this entity
            match attribute:

                case "test":
                    pass

    def tick(self, trigger_entity=None):
        super().tick(trigger_entity=trigger_entity)

    def draw(self):
        # draw a white rectangle
        pygame.draw.rect(
            self.game.screen,
            (255,255,255),
            self.rect
        )

class Cursor(Entity):
    def __init__(self, rect=Rect(0,0,10,10), game=None, updater=None, uuid=str(uuid.uuid4()),
                 sprite_path=None, scale_res=None, visible=True):

        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

        self.game.event_subscriptions[TickEvent].append(self.update_position)
    
    def draw(self):

        pygame.draw.rect(
            self.game.screen,
            (255,255,255),
            self.rect
        )

    def update_position(self, event):

        self.rect.center = pygame.mouse.get_pos()

class Player(PhysicsEntity):
    def __init__(self, health=100, weapon=None, gravity=0.05, velocity = Vector(0,0), max_velocity=Vector(50,50), friction=2, collidable_entities=[Floor], rect=None, game=None, updater=None, uuid=str(uuid.uuid4()),
                 sprite_path="fight/resources/cat.png", scale_res=None, visible=True):

        super().__init__(gravity=gravity, velocity=velocity, max_velocity=max_velocity, friction=friction, collidable_entities=collidable_entities, rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

        self.last_attack = 0

        if health is None:
            raise AttributeError("Missing health argument")

        self.health = health
        self.weapon = weapon

        self.game.event_subscriptions[TickEvent].append(self.handle_keys)
        

    def dict(self):

        data_dict = super().dict()

        data_dict["health"] = self.health

        if self.weapon is not None:
            data_dict["weapon"] = self.weapon.uuid
        else:
            data_dict["weapon"] = None

        return data_dict

    @classmethod
    def create(cls, entity_data, entity_id, game):

        entity_data["health"] = entity_data["health"]

        if entity_data["weapon"] is not None:
            entity_data["weapon"] = Unresolved(entity_data["weapon"])
        else:
            entity_data["weapon"] = None

        new_player = super().create(entity_data, entity_id, game)

        return new_player

    def update(self, update_data):

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

    def handle_keys(self, event):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:

            self.game.trigger_event(JumpEvent)
            
            if not self.airborne:
                self.velocity.y -= 10

        if keys[pygame.K_a]:
            self.velocity.x -= 1 * self.game.clock.get_time()

        if keys[pygame.K_d]:
            self.velocity.x += 1 * self.game.clock.get_time()

class Weapon(Entity):
    def __init__(self, ammo=None, max_ammo=None, attack_cooldown=None, owner=None, rect=None, game=None, updater=None, uuid=None,
                 sprite_path=None, scale_res=None, visible=True):
    
        print(scale_res)

        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

        if ammo is None:
            raise TypeError("Missing ammo argument")
        
        if max_ammo is None:
            raise TypeError("Missing max_ammo argument")
        
        if attack_cooldown is None:
            raise TypeError("Missing attack_cooldown argument")
        
        if owner is None:
            raise TypeError("Missing owner argument")

        self.ammo = ammo
        self.max_ammo = max_ammo
        self.attack_cooldown = attack_cooldown
        self.owner = owner

        self.game.event_subscriptions[TickEvent] += [
            self.follow_owner,
            self.follow_cursor
        ]

    def dict(self):
        # create a json serializable dictionary with all of this object's attributes

        # create the base entity's dict, then we add our own unique attributes on top
        data_dict = super().dict()

        data_dict["ammo"] = self.ammo
        data_dict["max_ammo"] = self.max_ammo
        data_dict["attack_cooldown"] = self.attack_cooldown
        data_dict["owner"] = self.owner.uuid

        return data_dict

    @classmethod
    def create(cls, entity_data, entity_id, game):
        # convert json entity data to object constructor arguments

        entity_data["ammo"] = entity_data["ammo"]
        entity_data["max_ammo"] = entity_data["max_ammo"]
        entity_data["attack_cooldown"] = entity_data["attack_cooldown"]
        entity_data["owner"] = Unresolved(entity_data["owner"])


        # call the base entity create method to do its own stuff and then return the actual object!!!!!
        new_player = super().create(entity_data, entity_id, game)

        return new_player

    def update(self, update_data):
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

    def follow_owner(self, event):
        self.rect = self.owner.rect.move(0,-50)

        self.game.network_update(
            update_type="update",
            entity_id=self.uuid,
            data={
                "rect": list(self.rect)
            }
        )

    def follow_cursor(self, event):
        mouse_pos = pygame.mouse.get_pos()

        #print(mouse_pos)

class Shotgun(Weapon):
    def __init__(self, ammo=2, max_ammo=2, attack_cooldown=1, owner=None, rect=None, game=None, updater=None, uuid=None,
                 sprite_path="fight/resources/shotgun.png", scale_res=(68,19), visible=True):

        super().__init__(ammo=ammo, max_ammo=max_ammo, attack_cooldown=attack_cooldown, owner=owner, rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

