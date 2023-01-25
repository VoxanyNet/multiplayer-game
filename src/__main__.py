import random
import argparse
import sys

from fight import Fight
from fightserver import FightServer

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server", dest="is_server", help="Run server", action="store_true")

args = parser.parse_args()

port = 55627

if args.is_server:

    server = FightServer()

    server.run(port=port)

else:
    game = Fight()

    game.run(server_ip="192.168.0.24",server_port=port)