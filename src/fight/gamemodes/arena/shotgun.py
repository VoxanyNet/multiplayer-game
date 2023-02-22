from fight.gamemodes.arena.weapon import Weapon

class Shotgun(Weapon):
    def __init__(self, ammo=2, max_ammo=2, attack_cooldown=1, owner=None, rect=None, game=None, updater=None, uuid=None,
                 sprite_path="fight/resources/shotgun.png", scale_res=(68,19), visible=True):

        super().__init__(ammo=ammo, max_ammo=max_ammo, attack_cooldown=attack_cooldown, owner=owner, rect=rect, game=game, updater=updater, sprite_path=sprite_path, uuid=uuid, scale_res=scale_res,
                         visible=visible)