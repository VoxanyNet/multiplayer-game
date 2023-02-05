class Event:
    pass

class LandedEvent(Event):
    def __init__(self, entity):
        self.entity = entity

class TickEvent(Event):
    pass 

class NewClientEvent(Event):
    def __init__(self, new_client_uuid=None):

        if new_client_uuid is None:
            raise TypeError("Missing 'new_client_uuid' argument")
    
        self.new_client_uuid = new_client_uuid