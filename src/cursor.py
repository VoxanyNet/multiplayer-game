import uuid

import pygame.key

from engine import Entity, Unresolved


class Cursor(Entity):
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
        return super().create(entity_data, entity_id, game)

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

    def tick(self):
        super().tick()

        last_tick_pos = (self.rect.x, self.rect.y)

        mouse_pos = pygame.mouse.get_pos()

        #print(last_tick_pos)

        #print(mouse_pos)
        
        if mouse_pos == last_tick_pos:
            return

        self.rect.x = mouse_pos[0]

        self.rect.y = mouse_pos[1]


        self.game.network_update(
            update_type="update",
            entity_id=self.uuid,
            data={
                "rect": list(self.rect)
            }
        )

        #print("tick")

        #print(keys)

    def draw(self):
        # draw a white rectangle
        pygame.draw.rect(
            self.game.screen,
            (255,255,255),
            self.rect
        )
