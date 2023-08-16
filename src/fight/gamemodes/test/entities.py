from typing import Optional, Union, Tuple, List, TYPE_CHECKING

import pygame
import pymunk
from pymunk import Shape, Body
from pymunk.constraints import DampedSpring

from engine.entity import Entity
from engine.gamemode_client import GamemodeClient
from engine.gamemode_server import GamemodeServer
from engine.tile import Tile
from engine.events import Tick

class MoveableTile(Tile):
    def __init__(self, body: Body, shape: Shape, game: GamemodeClient | GamemodeServer, updater: str, id: str | None = None):
        super().__init__(body, shape, game, updater, id)
        
        # we will add a constraint
        self.mouse_body = Body(mass=1, moment=1, body_type=pymunk.Body.KINEMATIC)

        self.game.space.add(self.mouse_body)

        self.game.event_subscriptions[Tick] += [
            self.follow_mouse,
            self.create_constraint,
            self.remove_constraints
        ]

    def draw(self):

        super().draw()

        if len(self.body.constraints) < 1:
            return 
        
        print(list(self.mouse_body.constraints)[0].a.position)
        print(pygame.mouse.get_pos())
        pygame.draw.line(
            self.game.screen, 
            (255,255,255),
            pygame.mouse.get_pos(),
            list(self.mouse_body.constraints)[0].a.position,
            width=5
        )
    def follow_mouse(self, event: Tick):

        self.mouse_body.position = pygame.mouse.get_pos()

    def create_constraint(self, event: Tick):

        # left clicking
        if not pygame.mouse.get_pressed()[0]:
            return
        
        # shape contains mouse
        if not self.shape.bb.contains_vect(
            pygame.mouse.get_pos()
        ):
            return

        # already have constraints
        if len(self.body.constraints) > 0:
            return

        print("created spring") 
        constraint = DampedSpring(
            a=self.body, 
            b=self.mouse_body, 
            anchor_a=self.body.center_of_gravity, 
            anchor_b=self.mouse_body.center_of_gravity,
            rest_length=100,
            stiffness=1000,
            damping=50
        )

        self.game.space.add(constraint)

        print("picking up!")
    
    def remove_constraints(self, event: Tick):
        
        if not pygame.mouse.get_pressed()[0]:
            
            for constraint in self.mouse_body.constraints:
                print("removing constraints")
                self.game.space.remove(constraint)