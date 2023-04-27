from headered_socket import HeaderedSocket
from entity import Entity

class Event:
    pass

class LandedEvent(Event):
    def __init__(self, entity: Entity):
        self.entity = entity

class TickEvent(Event):
    pass 

class NewClientEvent(Event):
    def __init__(self, new_client: HeaderedSocket):
    
        self.new_client = new_client

class DisconnectedClientEvent(Event):
    def __init__(self, disconnected_client: HeaderedSocket):

        self.disconnected_client = disconnected_client