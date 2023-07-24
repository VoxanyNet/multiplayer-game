from typing import Tuple, Union, TYPE_CHECKING

import pymunk

if TYPE_CHECKING:
    from engine.entity import Entity

class Tile:
    def __init__(
            self, 
            entity: "Entity", 
            position: Tuple[float, float],
            body_type: Union[pymunk.Body.STATIC, pymunk.Body.DYNAMIC, pymunk.Body.KINEMATIC], 
            velocity: Tuple[float, float] = (0,0), 
            angular_velocity: Tuple[float, float] = (0,0)
        ):

        self.entity = entity

        self.body = pymunk.Body(body_type=body_type)

        self.body.velocity = velocity
        self.body.position = position
        self.body.angular_velocity = angular_velocity

        self.shape = pymunk.Poly.create_box(self.body, (10,10))

        self.entity.game.space.add(self.body, self.shape)
    