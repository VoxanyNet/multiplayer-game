from typing import Type, TYPE_CHECKING

from engine.headered_socket import HeaderedSocket

if TYPE_CHECKING:
    from engine.entity import Entity
    from engine.physics_entity import PhysicsEntity

class Event:
    pass

class LandedEvent(Event):
    def __init__(self, entity: Type["PhysicsEntity"]):
        self.entity = entity

class TickEvent(Event):
    pass 

class NewClientEvent(Event):
    def __init__(self, new_client: HeaderedSocket):
    
        self.new_client = new_client

class DisconnectedClientEvent(Event):
    def __init__(self, disconnected_client_uuid: str):

        self.disconnected_client_uuid = disconnected_client_uuid

class GameTickStart(Event):
    pass

class GameTickComplete(Event):
    pass

class GameStart(Event):
    pass 

class ScreenCleared(Event):
    pass 

class ReceivedClientUpdates(Event):
    pass

class UpdatesLoaded(Event):
    pass

class ServerStart(Event):
    pass

class EntityAirborne(Event):
    def __init__(self, entity: Type["PhysicsEntity"]):

        self.entity = entity