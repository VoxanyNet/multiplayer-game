import random
import argparse
import sys
import os

from fight.gamemodes.arena.client import ArenaClient
from fight.gamemodes.arena.server import ArenaServer

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server", dest="is_server", help="Run server", action="store_true")
parser.add_argument("-m", "--music", dest="enable_music", help="Enable game music", action="store_true", default=False)

args = parser.parse_args()

print(args.enable_music)

port = 5593

if args.is_server:

    server = ArenaServer()

    server.run(port=port)

else:
    game = ArenaClient(f"http://192.168.0.24:{port}", fps=200, enable_music=args.enable_music)

    game.run()