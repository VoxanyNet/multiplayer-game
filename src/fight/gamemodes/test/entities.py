from typing import Dict, Optional, Type, Union, Tuple, List, TYPE_CHECKING
import time
import math

import pygame
import pymunk
from pymunk import Vec2d
from pymunk import Shape, Body
from pymunk.constraints import DampedSpring

from engine.entity import Entity
from engine import events
from engine.gamemode_client import GamemodeClient
from engine.gamemode_server import GamemodeServer
from engine.tile import Tile
from engine.events import Tick, NewEntity
from engine.unresolved import Unresolved
from engine.timeline import Timeline
from engine.drawable_entity import DrawableEntity
from engine.sprite_entity import SpriteEntity

class FreezableTileMaker(DrawableEntity, Entity):
    def __init__(
        self, 
        game: GamemodeClient | GamemodeServer, 
        updater: str, 
        id: str | None = None,
        draw_layer: Optional[int] = None
    ):
        
        Entity.__init__(
            self, 
            game=game, 
            updater=updater, 
            id=id
        )
        
        DrawableEntity.__init__(
            self, 
            game=game, 
            updater=updater, 
            draw_layer=draw_layer
        )
        
        
        self.game.event_subscriptions[events.KeyReturn] += [
            self.spawn_tile
        ]

        self.game.event_subscriptions[Tick] += [
            self.set_starting_point
        ]

        self.starting_point: Tuple[int, int] = [0,0]

        self.making_tile: bool = False

        self.last_spawn = 0

    def set_starting_point(self, event: Tick):
        
        if not pygame.key.get_pressed()[pygame.K_c]:
            self.making_tile = False 

            return

        if self.making_tile:
            return

        self.starting_world_point = self.game.adjusted_mouse_pos
        self.starting_screen_pount = pygame.mouse.get_pos()

        self.making_tile = True 
    
    def spawn_tile(self, event: events.KeyReturn):

        if not self.making_tile:
            return 
        
        if time.time() - self.last_spawn < 3:
            return
        
        body=pymunk.Body(
            body_type=pymunk.Body.STATIC
        )

        center = pygame.Rect([self.starting_world_point[0], self.starting_world_point[1], self.game.adjusted_mouse_pos[0] - self.starting_world_point[0], self.game.adjusted_mouse_pos[1] - self.starting_world_point[1]]).center

        body.position = center
    
        shape=pymunk.Poly.create_box(
            body=body,
            size=(
                self.game.adjusted_mouse_pos[0] - self.starting_world_point[0],
                self.game.adjusted_mouse_pos[1] - self.starting_world_point[1]
            )
        )

        shape.friction = 0.5
        shape.elasticity = 0.1
        
        tile = FreezableTile(
            body=body,
            shape=shape,
            game=self.game,
            updater=self.game.uuid
        )

        self.last_spawn = time.time()
    
    def draw(self):

        if not self.making_tile:
            return
        
        pygame.draw.rect(
            self.game.screen,
            color=(255,255,255),
            rect=[self.starting_screen_pount[0], self.starting_screen_pount[1], pygame.mouse.get_pos()[0] - self.starting_screen_pount[0], pygame.mouse.get_pos()[1] - self.starting_screen_pount[1]],
            width=1
        )

class Player(SpriteEntity, Tile):
    def __init__(
        self, 
        game: GamemodeClient | GamemodeServer, 
        updater: str, 
        active_sprite: Optional[pygame.Surface] = None,
        body: Body = None, 
        shape: Shape = None, 
        weapon: "Weapon" = None, 
        id: str | None = None, 
        draw_layer: int = 1,
        scale: int = 2
    ):
        
        if body is None or shape is None:
            body=pymunk.Body(
                mass=20,
                body_type=pymunk.Body.DYNAMIC
            )

            body.moment = pymunk.moment_for_box(
                body.mass,
                (68, 42)
            )

            body.position = game.screen.get_bounding_rect().center
    
            shape=pymunk.Poly.create_box(
                body=body,
                size=(68,42)
            )

            shape.friction = 0.5

        SpriteEntity.__init__(
            self=self,
            game=game, 
            updater=updater, 
            id=id, 
            draw_layer=draw_layer,
            active_sprite=active_sprite,
            scale=scale
        )
        
        Tile.__init__(
            self=self,
            body=body,
            shape=shape,
            game=game,
            updater=updater,
            id=id
        )

        self.weapon = weapon

        self.game.event_subscriptions[Tick] += [
            self.handle_keys,
            self.move_camera,
            self.advance_walk_cycle
        ]

        self.static_sprite = self.game.resources["resources/sprites/nyancat.png"]
        self.walk_timeline = Timeline(
            {
                0.08: self.game.resources["resources/timelines/nyancat/0.png"],
                0.16: self.game.resources["resources/timelines/nyancat/1.png"],
                0.24: self.game.resources["resources/timelines/nyancat/2.png"],
                0.32: self.game.resources["resources/timelines/nyancat/3.png"],
                0.40: self.game.resources["resources/timelines/nyancat/4.png"],
                0.48: self.game.resources["resources/timelines/nyancat/5.png"]
            },
            loop=True
        )

    def advance_walk_cycle(self, event: Tick):

        if abs(self.body.velocity.x) > 0:
            self.active_sprite = self.walk_timeline.get_frame(self.game.dt)
        else:
            self.active_sprite = self.static_sprite

    def draw(self):

        self.draw_onto_body()

    def move_camera(self, event: Tick):
        """Move camera if we get too close to the edge of the screen"""
        
        # the position of the player on the screen
        player_screen_pos = (
            self.body.position.x + self.game.camera_offset[0],
            self.body.position.y + self.game.camera_offset[1]
        )

        trigger_width = 500
        
        # if the player is within 100 pixels of the right side of the screen
        if player_screen_pos[0] > self.game.screen.get_width() - trigger_width:
            # move the camera so that the player is back to 100 pixels from the right of the screen
            need_to_move = (player_screen_pos[0] - (self.game.screen.get_width() - trigger_width))/2
            self.game.camera_offset[0] -= need_to_move
        
        # if the player is within 100 pixels of the left side of the screen (which will always be zero)
        if player_screen_pos[0] < 0 + trigger_width:
            # move the camera so that the player is back to 100 pixels from the left of the screen (which will always be zero)
            need_to_move = ((0 + trigger_width) - player_screen_pos[0])/2
            self.game.camera_offset[0] += need_to_move
        
        #print(self.game.camera_offset)
        
    def serialize(self) -> Dict[str, int | bool | str | list]:
        data_dict = {}
        data_dict.update(SpriteEntity.serialize(self))
        data_dict.update(Tile.serialize(self))

        if self.weapon:
            data_dict["weapon"] = self.weapon.id
        else:
            data_dict["weapon"] = None
        
        return data_dict
        
    @staticmethod
    def deserialize(entity_data: Dict[str, int | bool | str | list], entity_id: str, game: GamemodeClient | GamemodeServer) -> dict:
        
        if entity_data["weapon"]:
            entity_data["weapon"] = Unresolved(entity_data["weapon"])
        else:
            entity_data["weapon"] = None

        entity_data.update(SpriteEntity.deserialize(entity_data, entity_id, game))
        entity_data.update(Tile.deserialize(entity_data, entity_id, game))

        return entity_data
    
    def update(self, update_data: dict):
        SpriteEntity.update(self, update_data)
        Tile.update(self, update_data)
        
        for attribute_name, attribute_value in update_data.items():

            match attribute_name:
                
                case "weapon":

                    if attribute_value:
                        self.weapon = Unresolved(update_data["weapon"])
                    self.weapon = None
    
    def toggle_walk_cycle(self, event: Tick):

        if abs(self.body.velocity.x) > 0:
            self.walk_timeline.play() # reset timeline to first frame
            self.active_sprite = self.walk_timeline.current_frame
        
    def handle_keys(self, event: Tick):
        
        # move right
        if pygame.key.get_pressed()[pygame.K_d]:
            #print("right!")
            self.body.apply_force_at_world_point(
                (1000000,0),
                self.body.position
            )
        
        if pygame.key.get_pressed()[pygame.K_a]:
            #print("left")
            self.body.apply_force_at_world_point(
                (-1000000,0),
                self.body.position
            )
        
        if pygame.key.get_pressed()[pygame.K_SPACE]:

            if abs(self.body.velocity.y) > 0.1:
                return 
            
            self.body.apply_impulse_at_world_point(
                (0,-10000),
                self.body.position
            )

class Weapon(DrawableEntity, Tile):

    def __init__(self, 
        game: GamemodeClient | GamemodeServer, 
        updater: str, 
        clip_size: int,
        ammo: int,
        body: Body, 
        shape: Shape, 
        player: Optional[Player] = None, 
        id: str | None = None, 
        cooldown: int = 0, 
        last_shot: int = 0, 
        draw_layer: int = 1
    ): 

        
        DrawableEntity.__init__(
            self=self,
            game=game, 
            updater=updater, 
            id=id, 
            draw_layer=draw_layer
        )
        
        Tile.__init__(
            self=self,
            body=body,
            shape=shape,
            game=game,
            updater=updater,
            id=id
        )

        self.game.event_subscriptions[Tick] += [
            self.aim,
            self.follow_player,
            self.follow_cursor_on_circle
        ]

        self.game.event_subscriptions[events.MouseLeftClick] += [
            self.shoot
        ]

        self.player = player
        self.cooldown = cooldown
        self.last_shot = last_shot
        self.ammo = ammo 
        self.clip_size = clip_size
    
    def aim(self, event: Tick):
        if not self.player:
            return

        self.body.angle = math.atan2(
            self.game.adjusted_mouse_pos[1] - self.body.position.y,
            self.game.adjusted_mouse_pos[0] - self.body.position.x
        )
    
    def follow_player(self, event: Tick):
        if not self.player:
            return
        
        self.body.velocity = self.player.body.velocity
        
        self.body.position = (
            self.player.body.position.x + 50,
            self.player.body.position.y - 20
        )
    
    def shoot(self, event: events.MouseLeftClick):
        
        return

    def serialize(self) -> Dict[str, int | bool | str | list]:
        data_dict = {}
        data_dict.update(DrawableEntity.serialize(self))
        data_dict.update(Tile.serialize(self))

        if self.player:
            data_dict["player"] = self.player.id
        else:
            data_dict['player'] = None
        
        data_dict.update(
            {
                "cooldown": self.cooldown,
                "last_shot": self.last_shot,
                "clip_size": self.clip_size,
                "ammo": self.ammo
            }
        )

        return data_dict
    
    def update(self, update_data: dict):
        DrawableEntity.update(self, update_data)
        Tile.update(self, update_data)

        for attribute_name, attribute_value in update_data.items():

            match attribute_name:

                case "player":
                    
                    if attribute_value:
                        self.player = attribute_value
                    else:
                        self.player = None
                
                case "cooldown":
                    self.cooldown = attribute_value
                
                case "last_shot":
                    self.last_shot = attribute_value
    
    @staticmethod
    def deserialize(entity_data: Dict[str, int | bool | str | list], entity_id: str, game: GamemodeClient | GamemodeServer) -> dict:
        print("called")
        if entity_data["player"]:
            entity_data["player"] = Unresolved(entity_data["player"])
        else:
            entity_data["player"] = None
        
        entity_data["cooldown"] = entity_data["cooldown"]

        entity_data["last_shot"] = entity_data["last_shot"]
        
        entity_data.update(DrawableEntity.deserialize(entity_data, entity_id, game))
        entity_data.update(Tile.deserialize(entity_data, entity_id, game))

        return entity_data

    def follow_cursor_on_circle(self, event: Tick):
        
        if not self.player:
            return 
        
        # i stole this :)
        x1, y1 = self.player.body.position
        x2, y2 = self.game.adjusted_mouse_pos

        dx = x2 - x1
        dy = y2 - y1

        length = math.sqrt(dx**2 + dy**2)
        unit_dx = dx / length
        unit_dy = dy / length

        closest_x = x1 + 75 * unit_dx
        closest_y = y1 + 75 * unit_dy

        self.body.position = (closest_x, closest_y)
        
class Shotgun(Weapon, SpriteEntity):   
    def __init__(self, 
        game: GamemodeClient | GamemodeServer, 
        updater: str, 
        clip_size: int = 2, 
        ammo: int = 2, 
        player: Player | None = None, 
        body: Body = None, 
        shape: Shape = None, 
        id: str | None = None, 
        cooldown: int = 0.44, 
        last_shot: int = 0, 
        draw_layer: int = 1,
        active_sprite: Optional[pygame.Surface] = None,
        scale: int = 1.5
    ):
        
        if not body:
            body = Body(
                body_type=pymunk.Body.KINEMATIC
            )
        
        if not shape:
            shape = pymunk.Poly.create_box(
                body=body,
                size=(30,10)
            )
        
        
        SpriteEntity.__init__(
            self=self,
            game=game,
            updater=updater,
            draw_layer=draw_layer,
            active_sprite=active_sprite,
            id=id,
            scale=scale
        )

        Weapon.__init__(
            self=self,
            game=game,
            updater=updater,
            clip_size=clip_size,
            ammo=ammo,
            body=body,
            shape=shape,
            player=player,
            id=id,
            cooldown=cooldown,
            last_shot=last_shot,
            draw_layer=draw_layer
        )
        
        self.static_sprite = self.game.resources["resources/sprites/shotgun.png"]
        self.reload_timeline = Timeline(
            {
                0.04: self.game.resources["resources/timelines/shotgun_reload/0.png"],
                0.08: self.game.resources["resources/timelines/shotgun_reload/1.png"],
                0.12: self.game.resources["resources/timelines/shotgun_reload/2.png"],
                0.16: self.game.resources["resources/timelines/shotgun_reload/3.png"],
                0.20: self.game.resources["resources/timelines/shotgun_reload/4.png"],
                0.24: self.game.resources["resources/timelines/shotgun_reload/5.png"],
                0.28: self.game.resources["resources/timelines/shotgun_reload/4.png"],
                0.32: self.game.resources["resources/timelines/shotgun_reload/3.png"],
                0.36: self.game.resources["resources/timelines/shotgun_reload/2.png"],
                0.40: self.game.resources["resources/timelines/shotgun_reload/1.png"],
                0.44: self.game.resources["resources/timelines/shotgun_reload/0.png"]
            }
        )
        self.active_sprite = self.static_sprite

        self.game.event_subscriptions[Tick] += [
            self.handle_reload
        ]
    
    def serialize(self) -> Dict[str, int | bool | str | list]:

        data_dict = {}
        data_dict.update(SpriteEntity.serialize(self))
        data_dict.update(Weapon.serialize(self))

        return data_dict
    
    def draw(self):
        self.draw_onto_body()

    def update(self, update_data):
        SpriteEntity.update(self, update_data)
        Weapon.update(self, update_data)
        # update entity attributes with update_data
        # for example:
        # for attribute_name, attribute_value in update_data.items():

        #     match attribute_name:
                
        #         case "level":
        #             self.level = update_data["level"]
    
    
    def shoot(self, event: events.MouseLeftClick):

        if time.time() - self.last_shot < self.cooldown:
            return 

        self.last_shot = time.time()

        bullet = ShotgunBullet(
            game=self.game,
            updater=self.game.uuid
        )

        bullet.body.angle = math.atan2(
            self.game.adjusted_mouse_pos[1] - self.body.position.y,
            self.game.adjusted_mouse_pos[0] - self.body.position.x
        )

        mouse_pos = self.game.adjusted_mouse_pos

        # vector from weapon to mouse
        bullet_path_vector = Vec2d(
            x = mouse_pos[0] - self.body.position.x,
            y = mouse_pos[1] - self.body.position.y
        )

        bullet.body.position = (
            self.shape.bb.right + 20,
            self.body.position.y - 20
        )

        bullet.body.velocity = self.body.velocity + (bullet_path_vector.normalized() * 3000)

        bullet.sound.play()
        
        # begin reload animation
        self.reload_timeline.reset()
        self.active_sprite = self.reload_timeline.get_frame(0)
    
    def handle_reload(self, event: Tick):

        if time.time() - self.last_shot < self.cooldown:
            # progress reload animation
            self.active_sprite = self.reload_timeline.get_frame(self.game.dt)
            
            return  
        
        self.ammo = self.clip_size
        self.active_sprite = self.static_sprite


class Bullet(DrawableEntity, Tile):
    def __init__(
        self, 
        game: GamemodeClient | GamemodeServer, 
        updater: str, 
        weapon: Weapon = None, 
        body: Body = None, 
        shape: Shape = None, 
        id: str | None = None, 
        spawn_time = None, 
        draw_layer: int = 1
    ):

        body = Body(
            mass = 0.1,
            body_type=pymunk.Body.DYNAMIC
        )

        shape = pymunk.Poly.create_box(
            body=body,
            size=(5,2.5)
        )

        shape.friction = 0.5

        body.moment = pymunk.moment_for_box(
            body.mass,
            (10, 5)
        )

        DrawableEntity.__init__(
            self=self,
            game=game,
            updater=updater,
            draw_layer=draw_layer,
            id=id
        )

        Tile.__init__(
            self=self,
            body=body,
            shape=shape,
            game=game,
            updater=updater,
            id=id
        )

        self.game.event_subscriptions[Tick] += [
            self.despawn_bullet
        ]

        self.weapon = weapon

        if spawn_time:
            self.spawn_time = spawn_time
        else:
            self.spawn_time = time.time()
    
    def draw(self):
        self.debug_draw()

    def despawn_bullet(self, event: Tick):

        if time.time() - self.spawn_time > 1:
            self.kill()

    def serialize(self) -> Dict[str, int | bool | str | list]:
        data_dict = DrawableEntity.serialize(self) | Tile.serialize(self)

        if self.weapon:
            data_dict["weapon"] = self.weapon.id
        
        else:
            data_dict["weapon"] = None

        return data_dict

    def update(self, update_data: dict):
        DrawableEntity.update(self, update_data)
        Tile.update(self, update_data)

        for attribute_name, attribute_value in update_data.items():
            match attribute_name:
                case "weapon":

                    if attribute_value:
                        self.weapon = Unresolved(attribute_value)
                    else:
                        self.weapon = attribute_value
    
    @staticmethod
    def deserialize(entity_data: Dict[str, int | bool | str | list], entity_id: str, game: GamemodeClient | GamemodeServer) -> type[Tile]:
        
        if entity_data["weapon"]:
            entity_data["weapon"] = Unresolved(entity_data["weapon"])
        else:
            entity_data["weapon"] = None
        
        DrawableEntity.deserialize(entity_data, entity_id, game)
        Tile.deserialize(entity_data, entity_id, game)

        return entity_data

class ShotgunBullet(Bullet):
    def __init__(
        self, 
        game: GamemodeClient | GamemodeServer, 
        updater: str, 
        weapon: Weapon = None, 
        body: Body = None, 
        shape: Shape = None, 
        id: str | None = None, 
        spawn_time=None, 
        draw_layer: int = 1,
    ):
        super().__init__(
            game=game, 
            updater=updater, 
            weapon=weapon, 
            body=body, 
            shape=shape, 
            id=id, 
            spawn_time=spawn_time, 
            draw_layer=draw_layer 
        )

        if isinstance(self.game, GamemodeClient):
            self.sound = pygame.mixer.Sound("resources/sounds/shotgun.wav")
            self.sound.set_volume(0.10)

class FreezableTile(Tile, DrawableEntity):
    def __init__(
            self, 
            body: Body, 
            shape: Shape, 
            game: GamemodeClient | GamemodeServer, 
            updater: str, 
            id: str | None = None,
            draw_layer = 1
        ):
        
        DrawableEntity.__init__(
            self=self,
            game=game,
            updater=updater,
            draw_layer=draw_layer,
            id=id
        )

        Tile.__init__(
            self=self,
            body=body,
            shape=shape,
            game=game,
            updater=updater,
            id=id
        )

        self.game.event_subscriptions[Tick] += [
            self.create_constraint,
            self.freeze,
            self.unfreeze,
            self.move
        ]
    
    def serialize(self) -> Dict[str, int | bool | str | list]:
        data_dict = {} 
        data_dict.update(DrawableEntity.serialize(self))
        data_dict.update(Tile.serialize(self))

        return data_dict
    
    @staticmethod
    def deserialize(entity_data: Dict[str, int | bool | str | list], entity_id: str, game: type[GamemodeClient] | type[GamemodeServer]) -> dict:
        DrawableEntity.deserialize(
            entity_data=entity_data,
            entity_id=entity_id,
            game=game
        )

        Tile.deserialize(
            entity_data=entity_data,
            entity_id=entity_id,
            game=game
        )

        return entity_data
    
    def draw(self):
        self.debug_draw()

    def freeze(self, event: Tick):
        if not pygame.mouse.get_pressed()[2]:
            return
        
        # shape contains mouse
        if not self.shape.bb.contains_vect(
            self.game.adjusted_mouse_pos
        ):
            return

        self.body.body_type = pymunk.Body.STATIC
    
    def unfreeze(self, event: Tick):
        if not pygame.mouse.get_pressed()[1]:
            return
        
        # shape contains mouse
        if not self.shape.bb.contains_vect(
            self.game.adjusted_mouse_pos
        ):
            return
        
        self.body.body_type = pymunk.Body.DYNAMIC
        
        shape_width = self.shape.bb.right- self.shape.bb.left
        shape_height = self.shape.bb.top - self.shape.bb.bottom

        self.body.mass = 20
        moment = pymunk.moment_for_box(
            self.body.mass,
            (shape_width, shape_height)
        )

        self.body.moment = moment
    
    def move(self, event: Tick):
        if not pygame.mouse.get_pressed()[0]:
            return
        
        # shape contains mouse
        if not self.shape.bb.contains_vect(
            self.game.adjusted_mouse_pos
        ):
            return
        
        self.body.position = self.game.adjusted_mouse_pos
        self.body.velocity = (0,0)
        self.body.angle = 0

    def create_constraint(self, event: Tick):

        # left clicking
        if not pygame.mouse.get_pressed()[0]:
            return
        
        # shape contains mouse
        if not self.shape.bb.contains_vect(
            self.game.adjusted_mouse_pos
        ):
            return

class Background(DrawableEntity, Entity):
    def __init__(
        self, 
        game: GamemodeClient | GamemodeServer, 
        updater: str, 
        id: str | None = None, 
        draw_layer: int = 0,
    ):

        DrawableEntity.__init__(
            self=self,
            game=game,
            updater=updater,
            draw_layer=draw_layer,
            id=id
        )
    
    def draw(self):
        self.game.screen.fill(
            (
                0,
                51,
                102
            )
        )