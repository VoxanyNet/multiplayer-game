import time
import uuid
import socket
import json
from collections import defaultdict

import pygame

from engine import headered_socket
from engine.entity import Entity
from engine.helpers import get_matching_objects
from engine.exceptions import InvalidUpdateType, MalformedUpdate
from engine.events import TickEvent


class Game:
    def __init__(self, fps=60):
        self.clock = pygame.time.Clock()
        self.server = headered_socket.HeaderedSocket(socket.AF_INET, socket.SOCK_STREAM)
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
        self.waiting_for_updates = False
    
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

        # we do not send updates to the server if we did not RECEIVE updates last tick
        if self.waiting_for_updates:
            return

        updates_json = json.dumps(
            self.update_queue
        )

        self.server.send_headered(
            bytes(
                updates_json, "utf-8"
            )
        )

        self.update_queue = []

    def receive_network_updates(self):

        try:
            updates_json = self.server.recv_headered().decode("utf-8")

        except BlockingIOError:
            # this means that we need to wait until the next tick to receive our updates
            # this occurs when the server didnt respond fast enough with the updates

            self.waiting_for_updates = True # we use this to indicate that we should NOT send another update to the server
            
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
        
        self.waiting_for_updates = False # this indicates that we can safely send more updates to the server

        return

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

                if isinstance(function.__self__, Game):
                    pass
                
                else:
                    raise Exception("Only methods belonging to Game or Entity objects may be subscribers to events")

            
            function(event)


    def start(self, server_ip, server_port=5560):

        pygame.init()
        
        self.server.connect((server_ip, server_port))
        
        print("Connected to server")
        
        self.server.send_headered(
            bytes(self.uuid, "utf-8")
        )
        self.receive_network_updates()

        self.server.setblocking(False)

        print("Received initial state")
    
    def run(self, server_ip, server_port=5560):

        self.start(server_ip=server_ip, server_port=server_port)

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