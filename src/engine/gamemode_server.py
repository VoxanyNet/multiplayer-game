import socket
import json
from collections import defaultdict
from copy import deepcopy

import pygame
from flask import Flask, request, jsonify

from engine import headered_socket
from engine.headered_socket import Disconnected
from engine.exceptions import MalformedUpdate, InvalidUpdateType
from engine.events import TickEvent


class GamemodeServer:

    def __init__(self, tick_rate):

        self.flask_app = Flask(__name__)

        self.entities = {}
        self.entity_type_map = {}
        self.uuid = "server"
        self.tick_rate = tick_rate
        self.server_clock = pygame.time.Clock()
        self.update_queue = {}
        self.event_subscriptions = defaultdict(list)

        self.flask_app.add_url_rule("/player/<string:player_uuid>", self.add_player, methods=["POST"])
        self.flask_app.add_url_rule("/player/<string:player_uuid>", self.remove_player, methods=["DELETE"])
        self.flask_app.add_url_rule("/updates/<string:player_uuid>", self.send_updates, methods=["PUT"])
        self.flask_app.add_url_rule("/updates/<string:player_uuid>", self.receive_updates, methods=["GET"])
    
    def start(self, host, port):
        # initialization stuff

        pass

    def load_updates(self, updates):

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

        for entity in self.entities.values():
            entity.resolve()

    def lookup_entity_type_string(self, entity):

        for entity_type_string, entity_type in self.entity_type_map.items():
            if type(entity) is entity_type:
                return entity_type_string

    def add_player(self, player_uuid):
        
        # creates an entry in the update queue for the new player
        self.update_queue[player_uuid] = []

    
    def remove_player(self, player_uuid):
        
        del self.update_queue[player_uuid]
    
    def send_updates(self, player_uuid):

        incoming_updates = json.loads(
            request.json
        )

        for receiving_player_uuid in self.update_queue.keys():
            if receiving_player_uuid != player_uuid:
                self.update_queue[receiving_player_uuid] += incoming_updates

    def receive_updates(self, player_uuid):
        
        updates = deepcopy(self.update_queue[player_uuid])

        # receiving updates clears this player's update queue
        del self.update_queue[player_uuid]

        return jsonify(updates) 
            
    def run(self, host=socket.gethostname(), port=5560):

        self.start(host, port)

        self.flask_app.run()