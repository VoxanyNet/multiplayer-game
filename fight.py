from engine import Game, Entity, headered_socket

class Fight(Game):
    def __init__(self, fps):
        super().__init__(fps=fps)

    def handle_new_client(self, client):
        # the procedure we follow when a new client connects to the server

        super().handle_new_client(client)

        # send create updates for every entity
        for entity in self.entities:
            self.network_update("create", entity.uuid, data, entity_type=None)

