import socket
import json
from collections import defaultdict
from copy import deepcopy
from typing import List, Literal, Optional, Type, Dict, Union
import time

import pygame

from engine import headered_socket
from engine.headered_socket import Disconnected
from engine.exceptions import MalformedUpdate, InvalidUpdateType
from engine.events import TickEvent, Event, DisconnectedClientEvent, NewClientEvent, ReceivedClientUpdates, UpdatesLoaded, ServerStart, GameTickStart, GameTickComplete
from engine.entity import Entity


class GamemodeServer:

    def __init__(self, tick_rate: int, server_ip: str = socket.gethostname(), server_port: int = 5560):

        self.socket = headered_socket.HeaderedSocket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_sockets: Dict[str, headered_socket.HeaderedSocket] = {}
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
        self.server_ip = server_ip
        self.server_port = server_port

        self.event_subscriptions[TickEvent] += [
            self.accept_new_clients,
            self.receive_client_updates 
        ]

        self.event_subscriptions[ReceivedClientUpdates] += [
            self.load_updates
        ]

        self.event_subscriptions[UpdatesLoaded] += [
            self.send_client_updates
        ]

        self.event_subscriptions[ServerStart] += [
            self.enable_socket
        ]

        self.event_subscriptions[NewClientEvent] += [
            self.handle_new_client
        ]
    
    def enable_socket(self, event: ServerStart):
        self.socket.bind((self.server_ip, self.server_port))
        self.socket.setblocking(False)
        self.socket.listen(5)

        print("server online...")

    def trigger(self, event: Type[Event]):

        for function in self.event_subscriptions[type(event)]:
            if function.__self__.__class__.__base__ == GamemodeServer:
                # if the object this listener function belongs to has a base class that is GamemodeServer, then we don't need to check if we should run it
                # this is because we never receive other user's GamemodeServer objects
                pass
            # dont call function if the entity this function belongs to isnt ours
            elif function.__self__.updater != self.uuid:
                continue
            
            function(event) 

    def network_update(self, update_type: Union[Literal["create"], Literal["update"], Literal["delete"]], entity_id: str, destinations: List[str], data: dict = None, entity_type: str = None):
        # update_type: Union[Literal["create"], Literal["update"], Literal["delete"]], entity_id: str, data: dict = None, entity_type: str = None
        """Queue up a network update for specified client uuid(s)"""

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

    def load_updates(self, event: ReceivedClientUpdates):

        for update in deepcopy(self.updates_to_load):
            
            match update["update_type"]:

                case "create":

                    print("Received create update")

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

        self.trigger(UpdatesLoaded())

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
                
                self.send_client_updates()

    def handle_client_disconnect(self, event: DisconnectedClientEvent):
        
        disconnected_client_uuid = event.disconnected_client_uuid
        
        for entity_uuid, entity in self.entities.copy().items():

            entity: Entity

            if entity.updater == disconnected_client_uuid:
                del self.entities[entity_uuid]

                self.network_update(
                    update_type="delete",
                    entity_id=entity_uuid,
                    destinations=list(self.client_sockets.keys())
                )
        
        print(f"{disconnected_client_uuid} disconnected")
        
        del self.client_sockets[disconnected_client_uuid]

        print(self.update_queue)

        del self.update_queue[disconnected_client_uuid]

        print(self.update_queue)
        
    def accept_new_clients(self, event: TickEvent):

        try:
            new_client, address = self.socket.accept()

            self.trigger(NewClientEvent(new_client))

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

                self.trigger(DisconnectedClientEvent(sending_client_uuid))

                continue
            
            #self.validate_updates

            self.updates_to_load += incoming_updates

            for receiving_client_uuid, receiving_client in self.client_sockets.items():

                if sending_client_uuid is receiving_client_uuid:
                    continue

                self.update_queue[receiving_client_uuid] += incoming_updates
        
        self.trigger(ReceivedClientUpdates())

    def send_client_updates(self, event: Optional[ReceivedClientUpdates] = None):
        """Actually send queued network updates"""

        for receiving_client_uuid, updates in self.update_queue.copy().items():
            
            updates_json = json.dumps(updates)
            
            self.client_sockets[receiving_client_uuid].send_headered(
                bytes(updates_json, "utf-8")
            )
        
            self.update_queue[receiving_client_uuid] = []
            
    def run(self):
        
        self.trigger(ServerStart())

        last_tick = 0

        while True:   

            # receive and relay client updates as fast as possible
            # only tick at the specified tick rate
            if time.time() - last_tick >= 1/self.tick_rate:
                
                self.trigger(GameTickStart())

                self.trigger(TickEvent())

                self.trigger(GameTickComplete())

                last_tick = time.time()