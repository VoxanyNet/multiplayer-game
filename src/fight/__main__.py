import random
import argparse
import sys
import atexit
import socket

from fight.gamemodes.test.client import TestClient
from fight.gamemodes.test.server import TestServer

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server", dest="is_server", help="run server", action="store_true")
parser.add_argument("--ip", dest="ip", help="specifies the ip to connect / listen to", default=socket.gethostname())
parser.add_argument("--port", dest="port", help="specifies the port to connect / listen to ", default=5050)

args = parser.parse_args()

print(args.ip)

def report_server_tick_at_exit():
    print(server.tick_count)

def report_game_tick_at_exit():
    print(game.tick_count)

if args.is_server:

    atexit.register(report_server_tick_at_exit)

    server = TestServer(server_ip=args.ip, server_port=args.port)

    server.run()

else:

    atexit.register(report_game_tick_at_exit)
    
    game = TestClient(server_ip=args.ip, server_port=args.port)

    game.run()