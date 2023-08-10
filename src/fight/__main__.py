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
parser.add_argument("--port", dest="port", help="specifies the port to connect / listen to ", default=5050, type=int)
parser.add_argument("--compression", dest="enable_compression", help="enable network compression", action="store_true")

args = parser.parse_args()

print(args.ip)

def report_server_tick_at_exit():
    print(server.tick_count)

def report_game_tick_at_exit():
    print(game.tick_count)

if args.is_server:

    atexit.register(report_server_tick_at_exit)

    server = TestServer(server_ip=args.ip, server_port=args.port, network_compression=args.enable_compression)

    server.run()

else:

    atexit.register(report_game_tick_at_exit)
    
    game = TestClient(server_ip=args.ip, server_port=args.port, network_compression=args.enable_compression)

    game.run(network_tick_rate=30)