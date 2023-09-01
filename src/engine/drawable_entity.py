from typing import Dict, Optional, Union, TYPE_CHECKING
from engine.entity import Entity

if TYPE_CHECKING:
    from engine.gamemode_client import GamemodeClient
    from engine.gamemode_server import GamemodeServer

class DrawableEntity(Entity):
    def __init__(self, game: Union["GamemodeClient", "GamemodeServer"], updater: str, id: str | None = None, draw_layer: int = 0):
        super().__init__(game, updater, id)

        self.draw_layer = draw_layer
    
    def draw(self):
        # still getting used to more complex OOP concepts so this might be dumb
        # the reason i am adding this method is because i want to use type(DrawableEntity) to decide whether to draw something
        pass

    def serialize(self) -> Dict[str, int | bool | str | list]:
        data_dict = super().serialize()
        # serialize entity data to be json compatible
        data_dict.update(
          {
              "draw_layer": self.draw_layer
          }
        )
        return data_dict
    
    def update(self, update_data):
        super().update(update_data)
        # update entity attributes with update_data
        # for example:
        for attribute_name, attribute_value in update_data.items():

            match attribute_name:
                
                case "draw_layer":
                    self.draw_layer = attribute_value
    
    @classmethod
    def create(cls, entity_data: Dict[str, int | bool | str | list], entity_id: str, game: Union[type["GamemodeClient"], type["GamemodeServer"]]) -> type[Entity]:
        # deserialize all entity_data items
        # for example:
        entity_data["draw_layer"] = entity_data["draw_layer"]

        return super().create(entity_data, entity_id, game)