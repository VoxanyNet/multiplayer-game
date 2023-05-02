import socket
import json
from collections import defaultdict
from copy import deepcopy
from typing import Type

import pygame

from engine import headered_socket
from engine.headered_socket import Disconnected
from engine.exceptions import MalformedUpdate, InvalidUpdateType
from engine.events import TickEvent, Event, DisconnectedClientEvent, NewClientEvent
from engine.entity import Entity


class GamemodeServer:

    def __init__(self, tick_rate):

        self.socket = headered_socket.HeaderedSocket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_sockets = {}
        self.entities = {}
        self.entity_type_map = {
            "entity": Entity
        }
        self.updates_to_load = []
        self.uuid = "server"
        self.tick_rate = tick_rate
        self.server_clock = pygame.time.Clock()
        self.update_queue = defaultdict(list)
        self.event_subscriptions = defaultdict(list)

        self.event_subscriptions[TickEvent].append(
            self.accept_new_clients,
            self.receive_client_updates,
            self.send_client_updates
        )
    
    def start(self, host, port):
        self.socket.bind((host, port))
        self.socket.setblocking(False)
        self.socket.listen(5)

        print("server online...")

    def trigger(self, event: Type[Event]):

        for function in self.event_subscriptions[type(event)]:
            
            # dont call function if the entity this function belongs to isnt ours
            if function.__self__.updater != self.uuid:
                continue
            
            function(event)     

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

    def load_updates(self, event: TickEvent):

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
            entity: Entity

            entity.resolve()

    def lookup_entity_type_string(self, entity: Entity):

        for entity_type_string, entity_type in self.entity_type_map.items():
            if type(entity) is entity_type:
                return entity_type_string

    def handle_new_client(self, event: NewClientEvent):

        print("New connecting client")

        # make server socket blocking temporarily, because we need this data now
        self.socket.setblocking(True)

        client_uuid = event.new_client.recv_headered().decode("utf-8")

        self.socket.setblocking(False)

        self.client_sockets[client_uuid] = event.new_client

        if len(self.entities) == 0:
            
            empty_update = json.dumps([])

            event.new_client.send_headered(
                bytes(empty_update, "utf-8")
            )

            print("no entities, sending empty update")

        else:
            for entity in self.entities.values():

                entity: Entity

                entity_type_string = self.lookup_entity_type_string(entity)
                
                data = entity.dict()

                self.network_update(update_type="create", entity_id=entity.uuid, data=data, entity_type=entity_type_string, destinations=[client_uuid])
                
                self.send_client_updates(force=True)

    def handle_client_disconnect(self, event: DisconnectedClientEvent):
        
        client_uuid = event.disconnected_client_uuid
        
        for entity_uuid, entity in self.entities.copy().items():

            if entity.updater == client_uuid:
                del self.entities[entity_uuid]

                self.network_update(
                    update_type="delete",
                    entity_id=entity_uuid,
                    destinations=list(self.client_sockets.keys())
                )
        
        print(f"{client_uuid} disconnected")
        
        del self.client_sockets[client_uuid]

        print(self.update_queue)

        del self.update_queue[client_uuid]

        print(self.update_queue)
        
    def accept_new_clients(self, event: TickEvent):

        try:
            new_client, address = self.socket.accept()

            self.handle_new_client(new_client)

        except BlockingIOError: 
            pass
    
    def receive_client_updates(self, event: TickEvent):

        for sending_client_uuid, sending_client in self.client_sockets.copy().items():
            
            sending_client: headered_socket.HeaderedSocket
            
            try:
                incoming_updates = json.loads(
                    sending_client.recv_headered().decode("utf-8")
                )

            except BlockingIOError:
                continue
                
            except Disconnected:

                self.trigger(DisconnectedClientEvent(sending_client))

                continue
            
            #self.validate_updates

            self.updates_to_load += incoming_updates

            for receiving_client_uuid, receiving_client in self.client_sockets.items():

                if sending_client_uuid is receiving_client_uuid:
                    continue

                self.update_queue[receiving_client_uuid] += incoming_updates

    def send_client_updates(self, event: TickEvent):

        for receiving_client_uuid, updates in self.update_queue.copy().items():
            
            updates_json = json.dumps(updates)
            
            self.client_sockets[receiving_client_uuid].send_headered(
                bytes(updates_json, "utf-8")
            )
        
            self.update_queue[receiving_client_uuid] = []
            
    def run(self, host=socket.gethostname(), port=5560):

        self.start(host, port)

        while True:   

            # receive and relay client updates as fast as possible
            # only tick at the specified tick rate
            
            self.load_updates()

            if self.server_clock.get_time() >= 1/self.tick_rate:
                self.trigger(TickEvent())

                self.server_clock.tick()