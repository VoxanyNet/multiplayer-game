import pymunk

class Tile:
    def __init__(self, body: pymunk.Body) -> None:
        self.body = body
    