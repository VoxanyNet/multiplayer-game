from typing import Dict, Optional, Type, Union
from engine.entity import Entity
from engine.gamemode_client import GamemodeClient
from engine.gamemode_server import GamemodeServer

class ExampleEntity(Entity):

    def __init__(self, game: GamemodeClient | GamemodeServer, updater: str, id: str | None = None):
        super().__init__(game, updater, id)

        # add event listeners
        # for example:
        # self.game.event_subscriptions[Tick] += [
        #   self.check_collisions    
        # ]
    
    def serialize(self) -> Dict[str, int | bool | str | list]:
        data_dict = super().serialize()
        # serialize entity data to be json compatible
        # data_dict["velocity"] = [self.velocity.x, self.velocity.y]
    
    def update(self, update_data):
        super().update(update_data)
        # update entity attributes with update_data
        # for example:
        # self.velocity.x = entity_data["velocity"][0]
        # self.velocity.y = entity_data["velocity"][1]
    
    @classmethod
    def create(cls, entity_data: Dict[str, int | bool | str | list], entity_id: str, game: type[GamemodeClient] | type[GamemodeServer]) -> type[Entity]:
        # deserialize all entity_data items
        # for example:
        # entity_data["velocity"] = Vector(entity_data["vector"][0], entity_data["vector"][1])
        return super().create(entity_data, entity_id, game)