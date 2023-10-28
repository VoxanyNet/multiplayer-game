import random
import sys
import time
import uuid
import socket
import json
from collections import defaultdict
from typing import Union, Type, Dict, Literal, List, Optional, Tuple
import zlib
import pathlib

import pygame
from pygame import Rect
import pymunk
from pymunk import pygame_util
from rich import print

from engine import headered_socket
from engine.headered_socket import Disconnected
from engine.entity import Entity
from engine.tile import Tile
from engine.helpers import get_matching_objects
from engine.exceptions import InvalidUpdateType, MalformedUpdate
from engine.events import StartedTrackingUpdates, FinishedTrackingUpdates, Tick, Event, TickComplete, GameStart, TickStart, ScreenCleared, NetworkTick, ResourcesLoaded, ReceivedNetworkUpdates, SentNetworkUpdates, ParsedNetworkUpdates
from engine import events
from engine.drawable_entity import DrawableEntity


class GamemodeClient:
    def __init__(
        self, 
        server_ip: str = socket.gethostname(), 
        server_port: int = 5560, 
        network_compression: bool = True
    ): 
        
        pygame.init()
        pygame.mixer.init()
        
        self.update_history: List[List[dict]] = []
        self.server = headered_socket.HeaderedSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip: str = server_ip
        self.server_port: int = server_port
        self.uuid = str(uuid.uuid4())[0:4]
        self.outgoing_updates_queue: List[dict] = []
        self.incoming_updates_queue: List[dict] = []
        self.entity_type_map: Dict[str, Type[Entity]] = {}
        self.entities: Dict[str, Entity] = {}
        self.event_subscriptions = defaultdict(list)
        self.tick_count: int = 0
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)
        self.last_tick = time.time()
        self.resources: Dict[str, pygame.Surface] = {}
        self.dt = 0.1 # i am initializing this with 0.1 instead of 0 because i think it might break stuff
        self.sent_bytes = 0
        self.network_compression = network_compression
        self.adjusted_mouse_pos: List[int] = [0,0]
        self.camera_offset: List[int] = [0,0]
        self.screen: pygame.Surface = pygame.display.set_mode(
            [1280, 720],
            pygame.RESIZABLE
            #pygame.FULLSCREEN
        )

        self.options = pymunk.pygame_util.DrawOptions(self.screen)

        self.event_subscriptions[TickComplete] += [
            self.clear_screen
        ]

        self.event_subscriptions[ResourcesLoaded] += [
            self.connect
        ]
        
        self.event_subscriptions[ScreenCleared] += [
            self.draw_entities
        ]

        self.event_subscriptions[GameStart] += [
            self.start,
            self.load_resources
        ]

        self.event_subscriptions[Tick] += [
            self.increment_tick_counter,
            self.trigger_input_events,
            self.step_space,
            self.set_adjusted_mouse_pos,
            self.receive_network_updates, # it doesnt really matter when we receive network updates, they are parsed each network tick
        ]

        self.event_subscriptions[NetworkTick] += [
            self.send_network_updates,
            self.detect_entity_updates
        ]

        self.event_subscriptions[ParsedNetworkUpdates] += [
            self.set_entity_checkpoints
        ]
        
        self.event_subscriptions[TickStart] += [
            self.measure_dt
        ]

        self.event_subscriptions[FinishedTrackingUpdates] += [
            self.parse_incoming_updates
        ]

        self.entity_type_map.update(
            {
                "tile": Tile
            }
        )

    def load_resources(self, event: GameStart):
        for sprite_path in pathlib.Path("resources").rglob("*.png"):
            sprite_path = str(sprite_path)
            # replace windows file path backslashes with forward slashes
            sprite_path = sprite_path.replace("\\", "/")
            self.resources[sprite_path] = pygame.image.load(sprite_path)
        
        print(self.resources)

        self.trigger(ResourcesLoaded())

    def set_adjusted_mouse_pos(self, event: Tick):
        
        self.adjusted_mouse_pos = (
            pygame.mouse.get_pos()[0] - self.camera_offset[0],
            pygame.mouse.get_pos()[1] -  self.camera_offset[1]
        )
    def test_listener(self, event: Type[Event]):
        print(f"Test listener responding to {event}")
    
    def trigger_input_events(self, event: Tick):
        
        # mouse
        mouse = pygame.mouse.get_pressed()

        if mouse[0]:
            self.trigger(events.MouseLeftClick())
        
        if mouse[1]:
            self.trigger(events.MouseMiddleClick())
        
        if mouse[2]:
            self.trigger(events.MouseRightClick())
        
        # keyboard
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.trigger(events.KeyA())

        if keys[pygame.K_b]:
            self.trigger(events.KeyB())

        if keys[pygame.K_c]:
            self.trigger(events.KeyC())

        if keys[pygame.K_d]:
            self.trigger(events.KeyD())

        if keys[pygame.K_e]:
            self.trigger(events.KeyE())

        if keys[pygame.K_f]:
            self.trigger(events.KeyF())

        if keys[pygame.K_g]:
            self.trigger(events.KeyG())

        if keys[pygame.K_h]:
            self.trigger(events.KeyH())

        if keys[pygame.K_i]:
            self.trigger(events.KeyI())

        if keys[pygame.K_j]:
            self.trigger(events.KeyJ())

        if keys[pygame.K_k]:
            self.trigger(events.KeyK())

        if keys[pygame.K_l]:
            self.trigger(events.KeyL())

        if keys[pygame.K_m]:
            self.trigger(events.KeyM())

        if keys[pygame.K_n]:
            self.trigger(events.KeyN())

        if keys[pygame.K_o]:
            self.trigger(events.KeyO())

        if keys[pygame.K_p]:
            self.trigger(events.KeyP())

        if keys[pygame.K_q]:
            self.trigger(events.KeyQ())

        if keys[pygame.K_r]:
            self.trigger(events.KeyR())

        if keys[pygame.K_s]:
            self.trigger(events.KeyS())

        if keys[pygame.K_t]:
            self.trigger(events.KeyT())

        if keys[pygame.K_u]:
            self.trigger(events.KeyU())

        if keys[pygame.K_v]:
            self.trigger(events.KeyV())

        if keys[pygame.K_w]:
            self.trigger(events.KeyW())

        if keys[pygame.K_x]:
            self.trigger(events.KeyX())

        if keys[pygame.K_y]:
            self.trigger(events.KeyY())

        if keys[pygame.K_z]:
            self.trigger(events.KeyZ())
        
        if keys[pygame.K_RETURN]:
            self.trigger(events.KeyReturn())

        if keys[pygame.K_SPACE]:
            self.trigger(events.KeySpace())    
        
        if keys[pygame.K_PLUS]:
            self.trigger(events.KeyPlus())
        
        if keys[pygame.K_MINUS]:
            self.trigger(events.KeyMinus())

    def step_space(self, event: Tick):
        """Simulate physics for self.dt amount of time"""

        for _ in range(10):
            self.space.step(self.dt/10)
    
    def measure_dt(self, event: TickStart):
        """Measure the time since the last tick and update self.dt"""

        self.dt = time.time() - self.last_tick

        self.last_tick = time.time()

    def lookup_entity_type_string(self, entity: Union[Type[Entity], Type[type]]) -> str:
        """Find entity type's corresponding type string in entity_type_map"""

        entity_type_string = None

        for possible_entity_type_string, entity_type in self.entity_type_map.items():
            if type(entity) is entity_type or entity is entity_type: # this allows looking up an instance of an entity or just the class of an entity
                entity_type_string = possible_entity_type_string
        
        if entity_type_string ==  None:
            raise KeyError(f"Entity type {type(entity)} does not exist in entity type map")
    
        else:
            return entity_type_string

    def network_update(self, update_type: Union[Literal["create"], Literal["update"], Literal["delete"]], entity_id: str, data: dict = None, entity_type_string: str = None):

        if update_type not in ["create", "update", "delete"]:
            raise InvalidUpdateType(f"Update type {update_type} is invalid")

        if update_type == "create" and entity_type_string is None:
            raise MalformedUpdate("Create update requires 'entity_type_string' parameter")

        if update_type == "create" and entity_type_string not in self.entity_type_map:
            raise MalformedUpdate(f"Entity type {entity_type_string} does not exist in the entity type map")

        update = {
            "update_type": update_type,
            "entity_id": entity_id,
            "entity_type": entity_type_string,
            "data": data
        }

        self.outgoing_updates_queue.append(
            update
        )
    
    def increment_tick_counter(self, event: Tick):
        self.tick_count += 1

    def send_network_updates(self, event: NetworkTick):
        
        # we must send an updates list even if there are no updates
        # this is because the server will only give US updates if we do first
        
        self.update_history.append(self.outgoing_updates_queue)
        
        updates_json = json.dumps(
            self.outgoing_updates_queue
        )
        

        updates_json_bytes = bytes(
            updates_json, "utf-8"
        )

        if self.network_compression:

            updates_json_bytes = zlib.compress(
                updates_json_bytes, level=zlib.Z_BEST_COMPRESSION
            )

        self.server.send_headered(
            updates_json_bytes
        )

        self.sent_bytes += len(updates_json_bytes)

        self.outgoing_updates_queue = []


    def set_entity_checkpoints(self, event: ParsedNetworkUpdates):
        """Set entity update checkpoints after receiving updates from the server"""

        for entity in self.entities.values():
            entity.set_update_checkpoint()
        
        self.trigger(StartedTrackingUpdates())

    def detect_entity_updates(self, event: NetworkTick):
        """Detect all entity changes between when the checkpoint was set and now"""
        
        for entity in self.entities.values():
            entity.detect_updates()
        
        self.trigger(FinishedTrackingUpdates())
        
    # parse network updates -> start tracking updates ->  finish tracking updates -> parse network updates
        
    def receive_network_updates(self, event: Optional[NetworkTick] = None):

        # this method can either be directly invoked or be called by an event
        try:
            updates_json_bytes = self.server.recv_headered()
        except Disconnected:
            raise Disconnected()
            sys.exit(print("Server closed"))

        if updates_json_bytes is None: # this means that there are no new complete updates sent
            self.trigger(ReceivedNetworkUpdates())
            return

        if self.network_compression:
            try:
                updates_json_bytes = zlib.decompress(updates_json_bytes)
            except:
                pass
        
        updates_json = updates_json_bytes.decode("utf-8")


        updates = json.loads(
            updates_json
        )

        self.incoming_updates_queue += updates
        
        self.trigger(ReceivedNetworkUpdates())

    def parse_incoming_updates(self, event: FinishedTrackingUpdates):

        for update in self.incoming_updates_queue:

            match update["update_type"]:
                case "create":

                    entity_class = self.entity_type_map[
                        update["entity_type"]
                    ]

                    deserialized_data = entity_class.deserialize(
                        entity_data=update["data"], 
                        entity_id=update["entity_id"], 
                        game=self
                    )

                    entity_class(game=self, id=update["entity_id"], **deserialized_data)

                case "update":
                    
                    # sometimes entity updates will come in for entities that have killed because latency
                    if update["entity_id"] not in self.entities.keys():
                        continue

                    updating_entity = self.entities[
                        update["entity_id"]
                    ]

                    updating_entity.update(
                        update["data"]
                    )

                case "delete":

                    self.entities[update["entity_id"]].kill()

        for entity in self.entities.values():
            entity.resolve()

        self.incoming_updates_queue = []
        
        self.trigger(ParsedNetworkUpdates())
    
    def draw_entities(self, event: ScreenCleared):

        draw_order: Dict[int, List[Entity]] = defaultdict(list)

        for entity in self.entities.values():
            entity: Entity

            if not isinstance(entity, DrawableEntity):
                continue

            if entity.draw_layer is None:
                continue

            draw_order[entity.draw_layer].append(
                entity
            )
        
        sorted_draw_order = dict(sorted(draw_order.items(), key=lambda item: item[0]))

        for layer_entites in sorted_draw_order.values():
            for entity in layer_entites:
                entity.draw()

        #self.space.debug_draw(self.options)
        
        pygame.display.flip()

    def clear_screen(self, event: TickComplete):

        self.screen.fill((0,0,0))

        self.trigger(ScreenCleared())

    def trigger(self, event: Type[Event]):

        for function in self.event_subscriptions[type(event)]:
            if function.__self__.__class__.__base__ == GamemodeClient:
                # if the object this listener function belongs to has a base class that is GamemodeClient, then we don't need to check if we should run it
                # this is because we never receive other user's GamemodeClient objects

                # we need to do this check because the GamemodeClient object does not have an "updater" attribute
                pass
            # dont call function if the entity this function belongs to isnt ours
            elif function.__self__.updater != self.uuid:
                continue
            
            function(event)

    def start(self, event: GameStart):

        pass
        
    def connect(self, event: ResourcesLoaded):

        self.server.connect((self.server_ip, self.server_port))
        
        print("Connected to server")
        
        self.server.send_headered(
            bytes(self.uuid, "utf-8")
        )
        self.receive_network_updates()

        self.server.setblocking(False)

        print("Received initial state")
   
    def run(self, max_tick_rate: int, network_tick_rate: int):

        self.trigger(GameStart())

        running = True 

        last_game_tick = 0
        last_network_tick = 0

        while running:

            # tick at specified tick rate

            if pygame.key.get_pressed()[pygame.K_F4]:
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            if time.time() - last_game_tick >= 1/max_tick_rate:

                self.trigger(TickStart())

                self.trigger(Tick())

                self.trigger(TickComplete())

                last_game_tick = time.time()

            if time.time() - last_network_tick >= 1/network_tick_rate:
                self.trigger(NetworkTick())

                last_network_tick = time.time()
