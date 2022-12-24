import uuid
import socket
import threading
import json

import pygame

from engine import headered_socket
from engine.exceptions import InvalidUpdateType, MalformedUpdate


class Game:
    def __init__(self, fps=60):
        self.clock = pygame.time.Clock()
        # the socket that we use to communicate with the server
        self.server = headered_socket.HeaderedSocket(type=socket.AF_INET)
        # the uuid that identifies this client among other clients connected to a server
        self.uuid = str(uuid.uuid4())
        # list of updates to be sent every frame
        self.update_queue = []
        # a dictionary that maps entity types to strings
        self.entity_type_map = {}
        # dictionary mapping entity ids to the actual entity objects
        self.entities = {}
        # all of the client sockets
        self.client_sockets = []

        self.screen = pygame.display.set_mode([1280, 720])

        self.fps = fps

    def network_update(self, update_type, entity_id, data, entity_type=None):
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

        updates_json = json.dumps(
            self.update_queue
        )

        self.server.send_headered(
            bytes(
                updates_json, "utf-8"
            )
        )

    def receive_network_updates(self):
        # receive network updates from the server

        # a list of updates received from the server
        updates_json = self.server.recv_headered().decode("utf-8")

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
                    new_entity = entity_class.create(
                        update["data"], update["entity_id"], self
                    )
                    
                    # add the entity to the dictionary of entities
                    self.entities["entity_id"] = new_entity
                
                case "update":

                    # retrive the entity to be updated
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

    def draw_entities(self):
        for entity in self.entities:
            self.screen.blit(entity.sprite, entity.rect)

    def tick(self):
        # calls the tick method for every entity

        for entity in self.entities:

            # we only call the tick function on objects that we own
            # this prevents two clients from updating the same entity
            if entity.updater is not self.uuid:
                continue

            entity.tick()

    def host_server(self):
        # the socket that clients will connect to in order to receive updates from other clients
        server = headered_socket.HeaderedSocket(type=socket.AF_INET)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind(
            (socket.gethostname(), 5560)
        )

        server.listen(5)

        server.setblocking(False)

        while True:
            # accept new clients

            client, address = server.accept()

            self.handle_new_client(client)

            # for every client socket we read the updates they sent, then forward them to the rest of the clients
            for sending_client in self.client_sockets:

                update_data = sending_client.recv_headered()

                for receiving_client in self.client_sockets:
                    
                    # we dont send a clients update to itself
                    if sending_client is receiving_client:
                        continue
                    
                    # send the update data
                    receiving_client.send_headered(update_data)

    def handle_new_client(self, client):
        # operation we follow when a new client socket connects

        # add new client socket to the list of sockets
        self.client_sockets.append(client)

    def start(self, server_ip="127.0.0.1", server_port=5560):
        # everything that needs to occur when we start a client
        # this includes creating initial objects, connecting to a server, etc.

        # connect to a server
        self.server.connect((server_ip, server_port))

        # receive updates to get the client up to speed on the game state

    def run(self, host_server=True):
        # this function starts the game and begins the game loop

        # if we are hosting the server, we create a separate thread for running the server
        if host_server:
            server_thread = threading.Thread(target=self.host_server, daemon=True)

            server_thread.start()

        self.start()

        while True:
            # tick the game according to its fps value
            self.clock.tick(
                self.fps
            )

            self.tick()

            self.send_network_updates()

            #self.draw_entities()

            self.receive_network_updates()
