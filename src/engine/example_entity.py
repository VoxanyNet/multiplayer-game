import uuid

import pygame.key

from engine import Entity, Unresolved


class ExampleEntity(Entity):
    def __init__(self, example1=None, example2=None, rect=None, game=None, updater=None, uuid=str(uuid.uuid4()),
                 sprite_path=None, scale_res=None, visible=True):

        # initialize base entity
        super().__init__(rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)

        # checking for required arguments
        if example1 is None:
            raise AttributeError("Missing example1 argument")

        if example2 is None:
            raise AttributeError("Missing example2 argument")

        self.example1 = example1
        self.example2 = example2

    def dict(self):
        # create a json serializable dictionary with all of this object's attributes

        # create the base entity's dict, then we add our own unique attributes on top
        data_dict = super().dict()

        data_dict.update(
            {
                "example1": self.example1,
                "example2": self.example2.uuid  # when an attribute is an entity we send its uuid
            }
        )

        return data_dict

    @classmethod
    def create(cls, entity_data, entity_id, game):
        # convert json entity data to object constructor arguments

        entity_data["example1"] = entity_data["example1"]

        # when network updates reference an entity id, we use the "Unresolved" object
        entity_data["example2"] = Unresolved(entity_data["example2"])

        # base entity create method will extract the data it needs from the dictionary, then create the object
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

                case "example1":
                    self.example1 = update_data["example1"]

                case "example2":
                    # use "Unresolved" object when referencing entity id
                    self.example2 = Unresolved(update_data["example2"])

    def tick(self):
        # code to run every game tick

        pass
