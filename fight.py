from engine import Game, Entity, headered_socket

class Fight(Game):
    def __init__(self, fps):
        super().__init__(fps=fps)

        # maps update type strings to the appropriate function
        self.update_function_map.update(
            {
                "player_join": self.handle_player_join
            }
        )

    def handle_new_client(self, client):
        # the procedure we follow when a new client connects to the server

        for entity in self.entities:

            # we send different types of updates for different types of entities
            match type(entity):

                case

