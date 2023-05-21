import random
import time
import uuid
import socket
import json
from collections import defaultdict
from typing import Union, Type, Dict, Literal, List, Optional

import pygame
from pygame import Rect

from engine import headered_socket
from engine.entity import Entity
from engine.helpers import get_matching_objects
from engine.exceptions import InvalidUpdateType, MalformedUpdate
from engine.events import TickEvent, Event, GameTickComplete, GameStart, GameTickStart, ScreenCleared


class GamemodeClient:
    def __init__(self, tick_rate=60, server_ip: str = socket.gethostname(), server_port: int = 5560):
        self.server = headered_socket.HeaderedSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.server_port = server_port
        self.uuid = str(uuid.uuid4())
        self.update_queue = []
        self.entity_type_map = {}
        self.entities: Dict[str, Entity] = {}
        self.event_subscriptions = defaultdict(list)
        self.tick_counter = 0
        self.screen = pygame.display.set_mode(
            [1280, 720],
            pygame.RESIZABLE
            #pygame.FULLSCREEN
        )
        self.tick_rate = tick_rate

        self.event_subscriptions[GameTickComplete] += [
            self.clear_screen,
            self.send_network_updates,
            self.receive_network_updates
        ]

        self.event_subscriptions[ScreenCleared] += [
            self.draw_entities
        ]

        self.event_subscriptions[GameStart] += [
            self.start,
            self.connect
        ]
    
    def detect_collisions(self, rect: Rect, collection: Union[dict, list]) -> List[Type[Entity]]:

        colliding_entities = []

        for entity in get_matching_objects(collection, Entity):

            if rect.colliderect(entity.rect):
                colliding_entities.append(entity)

        return colliding_entities

    def lookup_entity_type_string(self, entity: Entity):

        for entity_type_string, entity_type in self.entity_type_map.items():
            if type(entity) is entity_type:
                return entity_type_string

    def network_update(self, update_type: Union[Literal["create"], Literal["update"], Literal["delete"]], entity_id: str, data: dict = None, entity_type: str = None):

        if update_type not in ["create", "update", "delete"]:
            raise InvalidUpdateType(f"Update type {update_type} is invalid")

        if update_type == "create" and entity_type is None:
            raise MalformedUpdate("Create update requires 'entity_type' parameter")

        if update_type == "create" and entity_type not in self.entity_type_map:
            raise MalformedUpdate(f"Entity type {entity_type} does not exist in the entity type map")

        update = {
            "update_type": update_type,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "data": data
        }

        self.update_queue.append(
            update
        )

    def send_network_updates(self, event: GameTickComplete):
        
        # we must send an updates list even if there are no updates
        # this is because the server will only give US updates if we do first

        updates_json = json.dumps(
            self.update_queue
        )

        self.server.send_headered(
            bytes(
                updates_json, "utf-8"
            )
        )

        self.update_queue = []

    def receive_network_updates(self, event: Optional[GameTickComplete] = None):
        # this method can either be directly invoked or be called by an event

        try:
            updates_json = self.server.recv_headered().decode("utf-8")

        except BlockingIOError:
            # this means that we need to wait until the next tick to receive our updates
            # this occurs when the server didnt respond fast enough with the updates
            
            return

        updates = json.loads(
            updates_json
        )

        for update in updates:

            match update["update_type"]:
                case "create":

                    entity_class = self.entity_type_map[
                        update["entity_type"]
                    ]

                    entity_class.create(
                        update["data"], update["entity_id"], self
                    )

                case "update":

                    updating_entity = self.entities[
                        update["entity_id"]
                    ]

                    updating_entity.update(
                        update["data"]
                    )

                case "delete":

                    del self.entities[
                        update["entity_id"]
                    ]

        for entity in self.entities.values():
            entity.resolve()

        return
    
    def draw_entities(self, event: ScreenCleared):

        for entity in self.entities.values():
            entity: Entity
            if entity.visible: 
                entity.draw()
        
        pygame.display.flip()

    def clear_screen(self, event: GameTickComplete):

        self.screen.fill((0,0,0))

        self.trigger(ScreenCleared())

    def trigger(self, event: Type[Event]):

        for function in self.event_subscriptions[type(event)]:
            if function.__self__.__class__.__base__ == GamemodeClient:
                # if the object this listener function belongs to has a base class that is GamemodeClient, then we don't need to check if we should run it
                # this is because we never receive other user's GamemodeClient objects
                pass
            # dont call function if the entity this function belongs to isnt ours
            elif function.__self__.updater != self.uuid:
                continue
            
            function(event)

    def start(self, event: GameStart):

        pygame.init()
        
    def connect(self, event: GameStart):

        self.server.connect((self.server_ip, self.server_port))
        
        print("Connected to server")
        
        self.server.send_headered(
            bytes(self.uuid, "utf-8")
        )
        self.receive_network_updates()

        self.server.setblocking(False)

        print("Received initial state")
   
    def run(self):

        self.trigger(GameStart())

        running = True 

        last_tick = 0

        while running:

            # draw as fast as possible
            # only tick at specified tick rate

            if pygame.key.get_pressed()[pygame.K_F4]:
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            if time.time() - last_tick >= 1/self.tick_rate:

                self.trigger(GameTickStart())

                #print(random.randint(0,10))
                self.trigger(TickEvent())

                self.trigger(GameTickComplete())

                last_tick = time.time()
            
            else:
                print("skipping tick")

            input("Press enter to advanced to next tick...")