import random
import argparse
import sys

from fight import Fight
from fightserver import FightServer

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server", dest="is_server", help="Run server", action="store_true")
parser.add_argument("-m", "--music", dest="enable_music", help="Enable game music", action="store_true", default=False)

args = parser.parse_args()

print(args.enable_music)

port = 5593

if args.is_server:

    server = FightServer(tick_rate=60)

    server.run(port=port)

else:
    game = Fight(fps=200, enable_music=args.enable_music)

    game.run(server_ip="192.168.0.24",server_port=port)