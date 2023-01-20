import time
import uuid
import socket
import threading
import multiprocessing
import json
from collections import defaultdict

import pygame

from engine import headered_socket
from engine.exceptions import InvalidUpdateType, MalformedUpdate


class Game:
    def __init__(self, fps=60, is_server=False):
        self.clock = pygame.time.Clock()
        # the host server socket
        self.hosting_socket = headered_socket.HeaderedSocket(socket.AF_INET, socket.SOCK_STREAM)
        # the socket that we use to communicate with the server
        self.server = headered_socket.HeaderedSocket(socket.AF_INET, socket.SOCK_STREAM)
        # the uuid that identifies this client among other clients connected to a server
        self.uuid = str(uuid.uuid4())
        # list of updates to be sent every frame
        self.update_queue = []
        # a dictionary that maps entity types to strings
        self.entity_type_map = {}
        # dictionary mapping entity ids to the actual entity objects
        self.entities = {}
        # all the client sockets
        self.client_sockets = []

        self.screen = pygame.display.set_mode([1280, 720])

        self.fps = fps

        self.is_server = is_server

    def network_update(self, update_type, entity_id, data, entity_type=None, empty=False):
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

        print("Start 'receive_network_updates'")

        # a list of updates received from the server
        updates_json = self.server.recv_headered().decode("utf-8")

        print("Got 'updates_json'")

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

    def host_server(self, port=5560):

        self.hosting_socket.bind(("127.0.0.1", port))

        # update 120 times a second
        server_clock = pygame.time.Clock()

        #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.hosting_socket.setblocking(False)

        self.hosting_socket.listen(5)

        print("Server online...")

        # this is a queue of the updates that need to be sent to
        # each client once they send an update to the server
        outgoing_updates = defaultdict(list)

        time.sleep(1000)

        while True:   

            # accept new clients
            try:
                client, address = self.hosting_socket.accept()

                self.handle_new_client(client)

            except BlockingIOError: 
                pass

            # we only send updates to clients that sent us updates
            clients_that_we_received_an_update_from = []

            # forward every incoming updates list to every other client
            for sending_client in self.client_sockets:

                try:
                    
                    # we need to load the json we received so we can combine it
                    # with the rest of the updates that need to be sent
                    incoming_updates = json.loads(
                        sending_client.recv_headered().decode("utf-8")
                    )
                
                except BlockingIOError:
                    # if we dont receive anything from the client we continue to the next one

                    continue

                # since this client sent us an update, they will receive all the updates
                # queued for them
                clients_that_we_received_an_update_from_lol.append(sending_client)

                for receiving_client in self.client_sockets:

                    # we dont send a clients update to itself
                    if sending_client is receiving_client:
                        continue

                    # merge incoming updates from sending_client with updates already queued
                    outgoing_updates[receiving_client] += incoming_updates
            
            print(dict(outgoing_updates))

            # once we have received incoming updates from all clients, we send them to other clients
            for receiving_client, updates in outgoing_updates.copy().items():
                
                # if we never received an update from a client, then we don't send them an update
                # they will eventually receive these updates once they send us an update
                if receiving_client not in clients_that_we_received_an_update_from_lol:

                    continue

                updates_json = json.dumps(updates)
                
                receiving_client.send_headered(
                    bytes(updates_json, "utf-8")
                )

                # clear the update queue for this particular client
                outgoing_updates[receiving_client] = []     

            server_clock.tick(1)   

    def handle_new_client(self, client):
        # operation we follow when a new client socket connects

        print("New connecting client")

        # add new client socket to the list of sockets
        self.client_sockets.append(client)
        
        # if there are no entities, we send an empty update list
        # we need this because the client requires an update list to be sent when connecting
        if len(self.entities) == 0:
            self.send_network_updates()

            print("sent empty update list")

            return

        # send create updates for every entity
        for entity in self.entities:

            # get string version of entity type
            for entity_type_string, entity_type in self.entity_type_map.items():
                if type(entity) is entity_type:
                    break  # this isn't really clear

            # get attributes of entity in dictionary form
            data = entity.dict()

            self.network_update(update_type="create", entity_id=entity.uuid, data=data, entity_type=entity_type_string)

    def start(self, server_ip="127.0.0.1", server_port=5560):
        # everything that needs to occur when we start a client
        # this includes creating initial objects, connecting to a server, etc.

        # wait for the server to start before connecting
        if self.is_server:
            time.sleep(3)

        # connect to a server
        self.server.connect((server_ip, server_port))

        print("Connected to server")

        # receive initial create updates for game state
        self.receive_network_updates()

        print("Received initial state")

    def run(self, port=5560):
        # this function starts the game and begins the game loop

        # if we are hosting the server, we create a separate thread for running the server
        if self.is_server:
            server_process = threading.Thread(target=self.host_server, daemon=True, kwargs={"port":port})

            server_process.start()

        self.start(server_port=port)

        while True:
            # tick the game according to its fps value
            self.clock.tick(
                self.fps
            )

            self.tick()

            self.send_network_updates()

            self.draw_entities()

            self.receive_network_updates()


