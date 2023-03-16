import socket
from collections import defaultdict
from copy import deepcopy
import logging

import pygame
from flask import Flask, request, jsonify

from engine import headered_socket
from engine.headered_socket import Disconnected
from engine.exceptions import MalformedUpdate, InvalidUpdateType
from engine.events import TickEvent


class GamemodeServer:

    def __init__(self):

        self.server = headered_socket.HeaderedSocket()
        self.entities = {}
        self.entity_type_map = {}
        self.update_queue = {}
        self.event_subscriptions = defaultdict(list)

    def load_updates(self, updates):

        for update in deepcopy(updates):
            
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

    def lookup_entity_type_string(self, entity):

        for entity_type_string, entity_type in self.entity_type_map.items():
            if type(entity) is entity_type:
                return entity_type_string

    def add_player(self, player_uuid):
        
        # if there are currently no clients connected, this client becomes the master
        if len(self.update_queue) == 0:
            is_master = True 
        
        else:
            is_master = False

        self.update_queue[player_uuid] = []

        initial_updates = []

        for entity in self.entities.values():

            entity_type_string = self.lookup_entity_type_string(entity)
            
            data = entity.dict()

            update = {
                "update_type": "create",
                "entity_id": entity.uuid,
                "entity_type": entity_type_string,
                "data": data
            }
            
            initial_updates.append(update)
        
        response = {
            "is_master": is_master,
            "initial_updates": initial_updates
        }

        return jsonify(response)

    
    def remove_player(self, player_uuid):
        
        del self.update_queue[player_uuid]

        return 204
    
    def send_updates(self, player_uuid):
        
        incoming_updates = request.json

        for receiving_player_uuid in self.update_queue.keys():
            if receiving_player_uuid != player_uuid:
                self.update_queue[receiving_player_uuid] += incoming_updates
        
        # load updates on the server side so new clients can receive current state
        self.load_updates(incoming_updates)

        return ("received updates", 201)

    def receive_updates(self, player_uuid):

        #print(len(self.update_queue))
        
        updates = deepcopy(self.update_queue[player_uuid])

        # receiving updates clears this player's update queue
        self.update_queue[player_uuid] = []

        return jsonify(updates) 
    
    def run(self, host=socket.gethostbyname(socket.gethostname()), port=5560):

        self.flask_app.run(host=host, port=port)