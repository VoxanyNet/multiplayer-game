import random
import argparse
import sys
import atexit

from fight.gamemodes.test.client import TestClient
from fight.gamemodes.test.server import TestServer

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server", dest="is_server", help="Run server", action="store_true")
parser.add_argument("-m", "--music", dest="enable_music", help="Enable game music", action="store_true", default=False)

args = parser.parse_args()

port = 5050

def report_server_tick_at_exit():
    print(server.tick_count)

def report_game_tick_at_exit():
    print(game.tick_count)

if args.is_server:

    atexit.register(report_server_tick_at_exit)

    server = TestServer(server_port=port)

    server.run()

else:

    atexit.register(report_game_tick_at_exit)
    
    game = TestClient(server_port=port)

    game.run(network_tick_rate=120)