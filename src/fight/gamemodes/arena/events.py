from engine.events import Event

class JumpEvent(Event):
    def __init__(self, entity):
        self.entity = entity