from typing import Union, Tuple

from pygame import Rect

from engine.entity import Entity
from engine.gamemode_client import GamemodeClient
from engine.gamemode_server import GamemodeServer
from engine.tile import Tile

class TestDynamic(Entity):
    def __init__(self, interaction_rect: Rect, game: Union["GamemodeClient", "GamemodeServer"], updater: str, id: str,
                 visible=True):
        
        super().__init__(interaction_rect=interaction_rect, game=game, updater=updater, id=id, visible=visible)

class TestStatic(Entity):

    def __init__(self, interaction_rect: Rect, game: Union["GamemodeClient", "GamemodeServer"], updater: str, id: str,
                 visible=True):
        
        super().__init__(interaction_rect=interaction_rect, game=game, updater=updater, id=id, visible=visible)

        tile = Tile(self, position=(500, 500), velocity=(0,0))