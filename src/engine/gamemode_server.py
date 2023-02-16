import socket
import json
from collections import defaultdict
from copy import deepcopy

import pygame

from engine import headered_socket
from engine.headered_socket import Disconnected
from engine.exceptions import MalformedUpdate, InvalidUpdateType
from engine.events import TickEvent


class GamemodeServer:

    def __init__(self, tick_rate):

        self.socket = headered_socket.HeaderedSocket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_sockets = {}
        self.entities = {}
        self.entity_type_map = {}
        self.updates_to_load = []
        self.uuid = "server"
        self.tick_rate = tick_rate
        self.server_clock = pygame.time.Clock()
        self.clients_that_sent_updates = []
        self.update_queue = defaultdict(list)
        self.event_subscriptions = defaultdict(list)
    
    def start(self, host, port):
        self.socket.bind((host, port))
        self.socket.setblocking(False)
        self.socket.listen(5)

        print("server online...")

    def trigger_event(self, event):

        for function in self.event_subscriptions[type(event)]:
            
            # dont call function if the entity this function belongs to isnt ours
            try:
                if function.__self__.updater != self.uuid:
                    continue
            
            # sometimes the function belongs to a Game object, which we dont need to check because know game methods in the subscriptions are always ours
            except AttributeError:

                if isinstance(function.__self__, GamemodeServer):
                    pass
                
                else:
                    raise Exception("Only methods belonging to Game or Entity objects may be subscribers to events")

            

    def network_update(self, update_type=None, entity_id=None, data=None, entity_type=None, destinations=None):

        if destinations is None:
            raise MalformedUpdate("Server side network updates require a destination")

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
        
        for destination in destinations:
            self.update_queue[destination].append(update)

    def load_updates(self):

        for update in deepcopy(self.updates_to_load):
            
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
            
        self.updates_to_load = []

        for entity in self.entities.values():
            entity.resolve()

    def lookup_entity_type_string(self, entity):

        for entity_type_string, entity_type in self.entity_type_map.items():
            if type(entity) is entity_type:
                return entity_type_string

    def handle_new_client(self, new_client):

        pass

    
    def handle_client_disconnect(self, client_uuid):

        pass
        
    def accept_new_clients(self):

        pass
    
    def receive_client_updates(self):

        pass

    def send_client_updates(self):

        pass
            
    def run(self, host=socket.gethostname(), port=5560):

        self.start(host, port)

        while True:   
            
            self.accept_new_clients()

            self.receive_client_updates() 

            self.send_client_updates()

            #print(self.update_queue)

            self.load_updates()

            self.trigger_event(TickEvent())

            self.server_clock.tick(self.tick_rate)