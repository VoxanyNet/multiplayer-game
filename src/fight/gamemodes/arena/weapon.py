import uuid

import pygame.key

from engine.entity import Entity
from engine.events import TickEvent
from engine.unresolved import Unresolved

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

    def follow_cursor(self, event):
        mouse_pos = pygame.mouse.get_pos()

        #print(mouse_pos)