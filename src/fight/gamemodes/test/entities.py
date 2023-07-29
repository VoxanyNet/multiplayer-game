from typing import Union, Tuple, List, TYPE_CHECKING

from pygame import Rect
import pymunk

from engine.entity import Entity
from engine.gamemode_client import GamemodeClient
from engine.gamemode_server import GamemodeServer
from engine.tile import Tile
from engine.tileentity import TileEntity, TileDict
from engine.events import LogicTick

class TestDynamic(TileEntity):
    
    def __init__(self, origin: [int, int], tile_layout: List[TileDict], interaction_rect: Rect, game: GamemodeClient | GamemodeServer, updater: str, id: str, visible=True):
        super().__init__(
            origin=origin, 
            tile_layout=tile_layout, 
            interaction_rect=interaction_rect, 
            game=game, 
            updater=updater, 
            id=id, 
            visible=visible
        )

        self.game.event_subscriptions[LogicTick] += [
            self.report_pos
        ]
    
    def report_pos(self, event: LogicTick):
        return
        print(f"pos: {self.tiles[0].body.position}")
    
class TestStatic(TileEntity):

    pass