import time
import uuid
import socket
import json
from collections import defaultdict

import pygame

from engine import headered_socket
from engine.exceptions import InvalidUpdateType, MalformedUpdate


class Game:
    def __init__(self, fps=60):
        self.clock = pygame.time.Clock()
        # the socket that we use to communicate with the server
        self.server = headered_socket.HeaderedSocket(socket.AF_INET, socket.SOCK_STREAM)
        # the uuid that identifies this client among other clients connected to a server
        self.uuid = str(uuid.uuid4())
        # list of updates to be sent next frame
        self.update_queue = []
        # a dictionary that maps entity types to strings
        self.entity_type_map = {}
        # dictionary mapping entity ids to the actual entity objects
        self.entities = {}
        # all the client sockets
        self.client_sockets = []

        self.screen = pygame.display.set_mode([1280, 720])

        self.fps = fps

        print(self.uuid)

    def lookup_entity_type_string(self, entity):
        # get string version of entity type
        for entity_type_string, entity_type in self.entity_type_map.items():
            if type(entity) is entity_type:
                return entity_type_string

    def network_update(self, update_type=None, entity_id=None, data=None, entity_type=None):
        # queues up an update to be sent on the soonest frame

        if update_type not in ["create", "update", "delete"]:
            raise InvalidUpdateType(f"Update type {update_type} is invalid")

        if update_type == "create" and entity_type is None:
            raise MalformedUpdate("Create update requires 'entity_type' parameter")

        # check that the entity type for the 'create' update actually exists
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
        # receive network updates from the server

        try:
            # a list of updates received from the server
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

                    # retrieve the matching entity type
                    entity_class = self.entity_type_map[
                        update["entity_type"]
                    ]

                    # create a new entity with the update data
                    # we also pass the game object for entity creation
                    entity_class.create(
                        update["data"], update["entity_id"], self
                    )

                case "update":

                    # retrieve the entity to be updated
                    updating_entity = self.entities[
                        update["entity_id"]
                    ]

                    # call the entity's update function with the update data
                    updating_entity.update(
                        update["data"]
                    )

                case "delete":

                    # remove the entity from the dictionary
                    del self.entities[
                        update["entity_id"]
                    ]

        # for all entities, resolve any uuids to actual objects
        for entity in self.entities.values():
            entity.resolve()
        
        self.waiting_for_updates = False # this indicates that we can safely send more updates to the server

        return

    def draw_entities(self):
        for entity in self.entities.values():
            if entity.visible: 
                entity.draw()
        
        pygame.display.flip()

    def tick(self):
        # calls the tick method for every entity 

        self.screen.fill((0,0,0))

        for entity in self.entities.values():

            # we only call the tick function on objects that we own
            # this prevents two clients from updating the same entity
            if entity.updater != self.uuid:
                continue

            entity.tick()

    def start(self, server_ip, server_port=5560):
        # everything that needs to occur when we start a client
        # this includes creating initial objects, connecting to a server, etc.
        
        # connect to a server
        self.server.connect((server_ip, server_port))
        
        print("Connected to server")

        # receive initial create updates for game state
        self.receive_network_updates()

        # only disable blocking once we have received the initial state
        self.server.setblocking(False)

        print("Received initial state")
    
    def run(self, server_ip, server_port=5560):
        # this function starts the game and begins the game loop

        self.start(server_ip=server_ip, server_port=server_port)

        running = True 

        while running:
            # tick the game according to its fps value
            self.clock.tick(
                self.fps
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.tick()
            
            self.draw_entities()

            self.send_network_updates()

            self.receive_network_updates()