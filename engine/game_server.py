import socket
import json
from collections import defaultdict

import pygame

from engine import headered_socket
from engine import Entity
from engine.exceptions import MalformedUpdate, InvalidUpdateType


class GameServer:

    def __init__(self):

        self.socket = headered_socket.HeaderedSocket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_sockets = []

        # we need to keep track of what entities are in the state for new client
        self.entities = {}

        self.entity_type_map = {}

        self.uuid = "server"

        self.server_clock = pygame.time.Clock()

        # this is a queue of updates to be sent to clients
        # this is reset every server tick
        # {client_socket : [update1, update2] }
        self.update_queue = defaultdict(list)
    
    def start(self, host, port):
        # what code needs to be executed when server starts
        # this will probably include creating the level and other initial entities
        self.socket.bind((host, port))

        self.socket.setblocking(False)

        self.socket.listen(5)

        print("server online...")

    def tick(self):
        # the server needs to update its own entities too!
        # calls the tick method for every entity

        for entity in self.entities:

            # we only call the tick function on objects that we own
            # this prevents two clients from updating the same entity
            if entity.updater != "server":
                continue

            entity.tick()
    
    def network_update(self, update_type=None, entity_id=None, data=None, entity_type=None, destinations=None):

        if destinations is None:
            raise MalformedUpdate("Server side network updates require a destination")

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
        
        # send the update to the specified destinations
        for destination in destinations:
            self.update_queue[destination].append(update)

    def load_updates(self, updates):
        # we need to read updates that come from the clients and load them to update our our entities state

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

    def lookup_entity_type_string(self, entity):
        # get string version of entity type
        for entity_type_string, entity_type in self.entity_type_map.items():
            if type(entity) is entity_type:
                return entity_type_string

    def handle_new_client(self, new_client):
        # operation we follow when a new client socket connects

        print("New connecting client")

        # add new client socket to the list of sockets
        self.client_sockets.append(new_client)
        
        # if there are no entities, we send an empty update list
        # we need this because the client requires an update list to be sent when connecting
        if len(self.entities) == 0:
            
            empty_update = json.dumps([])

            new_client.send_headered(
                bytes(empty_update, "utf-8")
            )

            print("no entities, sending empty update")

        else:
            # send create updates for every entity
            for entity in self.entities.values():

                entity_type_string = self.lookup_entity_type_string(entity)

                # get attributes of entity in dictionary form
                data = entity.dict()

                self.network_update(update_type="create", entity_id=entity.uuid, data=data, entity_type=entity_type_string, destinations=[new_client])
    
    def accept_new_clients(self):
        # accept new clients
        try:
            new_client, address = self.socket.accept()

            self.handle_new_client(new_client)

        except BlockingIOError: 
            pass
    
    def receive_client_updates(self):

        for sending_client in self.client_sockets:

            try:
                
                # these updates will be merged with updates from other users
                incoming_updates = json.loads(
                    sending_client.recv_headered().decode("utf-8")
                )
            
            except BlockingIOError:
                # if we dont receive anything from the client we continue to the next one

                continue

            # update the server's entity state with the new update
            self.load_updates(incoming_updates)

            # we need to ensure that players arent cheating
            #self.validate_updates

            for receiving_client in self.client_sockets:

                # we dont send a clients update to itself
                if sending_client is receiving_client:
                    continue

                # merge incoming updates from sending_client with updates already queued
                self.update_queue[receiving_client] += incoming_updates
    
    def send_client_updates(self):
        # once we have received incoming updates from all clients, we send them to other clients
        for receiving_client, updates in self.update_queue.copy().items():

            updates_json = json.dumps(updates)
            
            receiving_client.send_headered(
                bytes(updates_json, "utf-8")
            )

        # clear the update queue
        self.update_queue = defaultdict(list)
            
            #print("finished sending updates to clients")
    def run(self, host=socket.gethostname(), port=5560):

        self.start(host, port)

        while True:   
            
            self.accept_new_clients()

            self.receive_client_updates() 

            self.send_client_updates()           


            for index, entity in enumerate(self.entities.items()):
                print(index)
                print(f"{entity}")

            self.server_clock.tick(1)   