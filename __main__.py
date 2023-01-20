import random

from testgame import ExampleGame

game = ExampleGame(is_server=True)

game.run(port=random.randint(5000,5999))