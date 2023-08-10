from typing import Type, TYPE_CHECKING

from engine.headered_socket import HeaderedSocket

if TYPE_CHECKING:
    from engine.entity import Entity

class Event:
    pass

class Tick(Event):
    pass 

class NewClient(Event):
    def __init__(self, new_client: HeaderedSocket):
    
        self.new_client = new_client

class DisconnectedClient(Event):
    def __init__(self, disconnected_client_uuid: str):

        self.disconnected_client_uuid = disconnected_client_uuid

class TickStart(Event):
    pass

class TickComplete(Event):
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

class EntityCreated(Event):
    def __init__(self, new_entity: Type["Entity"]):
        self.new_entity = new_entity

class NetworkTick(Event):
    pass