import uuid

import pygame.key

from engine.physics_entity import PhysicsEntity
from engine.vector import Vector
from engine.unresolved import Unresolved
from engine.events import TickEvent
from fight.gamemodes.arena.events import JumpEvent


class Player(PhysicsEntity):
    def __init__(self, health=100, weapon=None, gravity=0.05, velocity = Vector(0,0), max_velocity=Vector(50,50), friction=2, rect=None, game=None, updater=None, uuid=str(uuid.uuid4()),
                 sprite_path=None, scale_res=None, visible=True):

        super().__init__(gravity=gravity, velocity=velocity, max_velocity=max_velocity, friction=friction, rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
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