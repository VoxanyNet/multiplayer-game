import sys
import uuid

from engine import Vector
from engine import Entity

class PhysicsEntity(Entity):
    def __init__(self, gravity=None, velocity = Vector(0,0), max_velocity = None, friction=2, rect=None, game=None, updater=None, uuid=str(uuid.uuid4()), sprite_path=None, scale_res=None, visible=True):

        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res, visible=visible)
        if gravity is None:
            raise TypeError("Missing gravity argument")
        
        if velocity is None:
            raise TypeError("Missing velocity argument")
        
        if friction is None:
            raise TypeError("Missing friction argument")

        self.velocity = velocity
        self.gravity = gravity
        self.max_velocity = max_velocity
        self.friction = friction
        self.airborne = False

        self.game.event_subscriptions["tick"] += [
            self.tick,
            self.move_x_axis,
            self.move_y_axis,
            self.apply_gravity,
            self.apply_friction
        ]

        self.game.event_subscriptions["landed"] += [
            self.bounce
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
    def create(cls, entity_data, entity_id, game):
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
    
    def update(self, update_data):

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

    def move_x_axis(self, trigger_entity=None):

        projected_rect_x = self.rect.move(
            Vector(self.velocity.x, 0)
        )

        colliding_entities = self.game.detect_collisions(projected_rect_x, self.game.entities)

        if self in colliding_entities:
            del colliding_entities[colliding_entities.index(self)]

        if len(colliding_entities) != 0:

            # we only use the first entity in the list for collisions
            colliding_entity = colliding_entities[0]

            print(colliding_entity)

            # entity came in moving left
            if projected_rect_x.right < colliding_entity.rect.right and self.rect.right > colliding_entity.rect.right:
                self.rect.right = colliding_entity.rect.left
            
            # entity came in moving right
            elif projected_rect_x.left > colliding_entity.rect.left and self.rect.left < colliding_entity.rect.left:
                self.rect.left = colliding_entity.rect.right

                print("epic")
        
        else:

            self.rect.x = projected_rect_x.x

    def move_y_axis(self, trigger_entity=None):
        
        projected_rect_y = self.rect.move(
            Vector(0, self.velocity.y)
        )

        colliding_entities = self.game.detect_collisions(projected_rect_y, self.game.entities)

        if self in colliding_entities:
            del colliding_entities[colliding_entities.index(self)]

        if len(colliding_entities) != 0:

            # we only use the first entity in the list for collisions
            colliding_entity = colliding_entities[0]

            #  new rect bottom is lower than the collidinng rect's top and the old rect bottom is higher than the colliding rect top
            if (projected_rect_y.bottom >= colliding_entity.rect.top) and (self.rect.bottom <= colliding_entity.rect.top):

                self.rect.bottom = colliding_entity.rect.top

                self.velocity.y = 0

                self.airborne = False

                self.game.trigger_event("landed", self)

                #sys.exit()
            
            # entity came in moving up
            elif projected_rect_y.top <= colliding_entity.rect.bottom and self.rect.top >= colliding_entity.rect.bottom:
                self.rect.top = colliding_entity.rect.bottom

                self.airborne = True
        else:
            self.rect.y = projected_rect_y.y

            self.airborne = True

    def apply_friction(self, trigger_entity=None):

        if abs(self.velocity.x) > 0:

            self.velocity.x *= (0.05 * self.game.clock.get_time() )
            

    def apply_gravity(self, trigger_entity=None):

        if self.airborne:
            self.velocity.y += (self.gravity * self.game.clock.get_time())

    def bounce(self, trigger_entity=None):
        
        if trigger_entity.uuid != self.uuid:
            return
        
        self.velocity.y *= -0.25

    def tick(self, trigger_entity=None):

        self.game.network_update(
            update_type="update",
            entity_id=self.uuid,
            data= {
                "rect": list(self.rect)
            }
        )