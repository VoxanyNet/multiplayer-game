from fight.gamemodes.test.entities import Rocket, RPG, EntitySpawner, FreezableTile, FreezableTileMaker, Player, Weapon, Bullet, Background, Shotgun, ShotgunBullet

entity_type_map = {
    "freezable_tile": FreezableTile,
    "freezable_tile_maker": FreezableTileMaker,
    "player": Player,
    "weapon": Weapon,
    "bullet": Bullet,
    "background": Background,
    "shotgun": Shotgun,
    "shotgun_bullet": ShotgunBullet,
    "entity_spawner": EntitySpawner,
    "rpg": RPG,
    "rocket": Rocket
}