from typing import Tuple, Union, TYPE_CHECKING

import pymunk

if TYPE_CHECKING:
    from engine.entity import Entity

class Tile:
    def __init__(
            self, 
            entity: "Entity", 
            body: pymunk.Body,
            shape: pymunk.Shape
        ):

        self.entity = entity
        self.body = body 
        self.shape = shape

        self.shape = pymunk.Poly.create_box(self.body, (10,10))

        self.entity.game.space.add(self.body, self.shape)
    