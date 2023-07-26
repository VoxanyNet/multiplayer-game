from typing import Union, Tuple

from pygame import Rect
import pymunk

from engine.entity import Entity
from engine.gamemode_client import GamemodeClient
from engine.gamemode_server import GamemodeServer
from engine.tile import Tile
from engine.tileentity import TileEntity
from engine.events import LogicTick

class TestDynamic(TileEntity):
    
    def __init__(self, interaction_rect: Rect, game: GamemodeClient | GamemodeServer, updater: str, id: str, visible=True):
        super().__init__(interaction_rect, game, updater, id, visible)

        body = pymunk.Body(mass=2, moment=1, body_type=pymunk.Body.DYNAMIC)
        body.position = (500, 500)
        shape = pymunk.Poly.create_box(body=body, size=(20,20))

        tile = Tile(self, body=body, shape=shape)

        self.tiles.append(tile)

        self.game.event_subscriptions[LogicTick] += [
            self.report_pos
        ]
    
    def report_pos(self, event: LogicTick):
        return
        print(f"pos: {self.tiles[0].body.position}")
    
class TestStatic(TileEntity):

    pass