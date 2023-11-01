from typing import TYPE_CHECKING

from engine.events import Event

if TYPE_CHECKING:
    from fight.gamemodes.test.entities import Bullet, Player

class BulletHit(Event):
    def __init__(
        self,
        bullet: Bullet,
        player: Player
    ):
        self.bullet = bullet
        self.player = player
        