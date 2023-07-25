from typing import Union, Tuple

from pygame import Rect
import pymunk

from engine.entity import Entity
from engine.gamemode_client import GamemodeClient
from engine.gamemode_server import GamemodeServer
from engine.tile import Tile
from engine.tileentity import TileEntity

class TestDynamic(TileEntity):
    
    pass 
class TestStatic(TileEntity):

    pass