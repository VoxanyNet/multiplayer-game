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

class ResourcesLoaded(Event):
    pass 

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

class NewEntity(Event):
    def __init__(self, new_entity: Type["Entity"]):
        self.new_entity = new_entity

class KeyA(Event):
    pass

class KeyB(Event):
    pass

class KeyC(Event):
    pass

class KeyD(Event):
    pass

class KeyE(Event):
    pass

class KeyF(Event):
    pass

class KeyG(Event):
    pass

class KeyH(Event):
    pass

class KeyI(Event):
    pass

class KeyJ(Event):
    pass

class KeyK(Event):
    pass

class KeyL(Event):
    pass

class KeyM(Event):
    pass

class KeyN(Event):
    pass

class KeyO(Event):
    pass

class KeyP(Event):
    pass

class KeyQ(Event):
    pass

class KeyR(Event):
    pass

class KeyS(Event):
    pass

class KeyT(Event):
    pass

class KeyU(Event):
    pass

class KeyV(Event):
    pass

class KeyW(Event):
    pass 

class KeyX(Event):
    pass

class KeyY(Event):
    pass

class KeyZ(Event):
    pass

class KeySpace(Event):
    pass

class KeyReturn(Event):
    pass

class KeyPlus(Event):
    pass

class KeyMinus(Event):
    pass

class MouseLeftClick(Event):
    pass

class MouseMiddleClick(Event):
    pass 

class MouseRightClick(Event):
    pass