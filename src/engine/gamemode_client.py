import time
import uuid
import socket
import json
from collections import defaultdict

import pygame
import pymunk
import requests

from engine import headered_socket
from engine.entity import Entity
from engine.helpers import get_matching_objects
from engine.exceptions import InvalidUpdateType, MalformedUpdate
from engine.events import TickEvent


class GamemodeClient:
    def __init__(self, server_address, fps=60):
        self.clock = pygame.time.Clock()
        self.server = requests.Session()
        self.is_master = True # the update server will tell the first client to connect to become master
        self.server_address = server_address
        self.uuid = str(uuid.uuid4())
        self.update_queue = []
        self.entity_type_map = {}
        self.entities = {}
        self.event_subscriptions = defaultdict(list)
        self.event_subscriptions[TickEvent].append(self.clear_screen)
        self.tick_counter = 0
        self.screen = pygame.display.set_mode(
            [1280, 720],
            pygame.RESIZABLE
            #pygame.FULLSCREEN
        )
        self.fps = fps
    
    def detect_collisions(self, rect, collection):

        colliding_entities = []

        for entity in get_matching_objects(collection, Entity):

            if rect.colliderect(entity.rect):
                colliding_entities.append(entity)

        return colliding_entities

    def lookup_entity_type_string(self, entity):

        for entity_type_string, entity_type in self.entity_type_map.items():
            if type(entity) is entity_type:
                return entity_type_string

    def network_update(self, update_type=None, entity_id=None, data=None, entity_type=None):

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

    def send_network_updates(self):
        
        # we must send an updates list even if there are no updates
        # this is because the server will only give US updates if we do first

        self.server.put(
            f"{self.server_address}/updates/{self.uuid}",
            json=self.update_queue
        )

        self.update_queue = []

    
    def load_updates(self, updates):

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

    def receive_network_updates(self):

        updates = requests.get(f"{self.server_address}/updates/{self.uuid}").json()

        self.load_updates(updates)
        
    def draw_entities(self):
        for entity in self.entities.values():
            if entity.visible: 
                entity.draw()
        
        pygame.display.flip()

    def clear_screen(self, event):

        self.screen.fill((0,0,0))

    def tick(self):

        self.screen.fill((0,0,0))

        for entity in self.entities.values():

            if entity.updater != self.uuid:
                continue

            entity.tick()

    def trigger_event(self, event):

        for function in self.event_subscriptions[type(event)]:
            
            # dont call function if the entity this function belongs to isnt ours
            try:
                if function.__self__.updater != self.uuid:
                    continue
        
            # sometimes the function belongs to a Game object, which we dont need to check because know game methods in the subscriptions are always ours
            except AttributeError:

                if isinstance(function.__self__, GamemodeClient):
                    pass
                
                else:
                    raise Exception("Only methods belonging to Game or Entity objects may be subscribers to events")

            
            function(event)


    def start(self):
        
        pygame.init()
        
    def connect(self):

        resp = self.server.post(
            f"{self.server_address}/player/{self.uuid}"
        ).json()

        self.is_master = resp["is_master"]

        self.load_updates(
            resp["initial_updates"]
        )
    
    def run(self):
        
        self.connect()

        self.start()

        running = True 

        while running:
            if pygame.key.get_pressed()[pygame.K_F4]:
                running = False

            self.clock.tick(
                self.fps
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.trigger_event(TickEvent())
            
            self.draw_entities()

            self.send_network_updates()

            self.receive_network_updates()