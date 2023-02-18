import socket
import json
from collections import defaultdict
from copy import deepcopy

import pygame
from flask import Flask, request

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
        self.update_queue = defaultdict(list)
        self.event_subscriptions = defaultdict(list)

        self.flask_app.add_url_rule
    
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

        pass

    
    def remove_player(self, player_uuid):

        pass
    
    def receive_player_updates(self, player_uuid):

        pass

    def send_player_updates(self, player_uuid):

        pass
            
    def run(self, host=socket.gethostname(), port=5560):

        self.start(host, port)

        self.flask_app.run()