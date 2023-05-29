import random
import argparse
import sys

from fight.gamemodes.arena.client import ArenaClient
from fight.gamemodes.arena.server import ArenaServer

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server", dest="is_server", help="Run server", action="store_true")
parser.add_argument("-m", "--music", dest="enable_music", help="Enable game music", action="store_true", default=False)

args = parser.parse_args()

print(args.enable_music)

if args.is_server:

    server = ArenaServer(tick_rate=60)

    server.run()

else:
    game = ArenaClient(tick_rate=60, enable_music=args.enable_music)

    game.run()