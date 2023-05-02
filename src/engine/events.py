from typing import Type

from engine.headered_socket import HeaderedSocket
from engine.entity import Entity
from engine.physics_entity import PhysicsEntity

class Event:
    pass

class LandedEvent(Event):
    def __init__(self, entity: Type[PhysicsEntity]):
        self.entity = entity

class TickEvent(Event):
    pass 

class NewClientEvent(Event):
    def __init__(self, new_client: HeaderedSocket):
    
        self.new_client = new_client

class DisconnectedClientEvent(Event):
    def __init__(self, disconnected_client: HeaderedSocket):

        self.disconnected_client = disconnected_client

class GameTickStart(Event):
    pass

class GameTickComplete(Event):
    pass

class GameStart(Event):
    pass 
