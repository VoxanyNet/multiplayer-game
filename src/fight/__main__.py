import random
import argparse
import sys
import atexit
import socket
import json

from fight.gamemodes.test.client import Client
from fight.gamemodes.test.server import Server

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server", dest="is_server", help="run server", action="store_true")
parser.add_argument("--ip", dest="ip", help="specifies the ip to connect / listen to", default=socket.gethostname())
parser.add_argument("--port", dest="port", help="specifies the port to connect / listen to ", default=5560, type=int)
parser.add_argument("--compression", dest="enable_compression", help="enable network compression", action="store_true")

args = parser.parse_args()

print(args.ip)

def report_server_tick_at_exit():
    print(server.tick_count)

def report_game_tick_at_exit():
    print(game.tick_count)

def save_update_history():
    with open("updates.json", "w") as file:
        json.dump(game.update_history, file, indent=4)

if args.is_server:

    atexit.register(report_server_tick_at_exit)

    server = Server(server_ip=args.ip, server_port=args.port, network_compression=args.enable_compression)

    server.run(max_tick_rate=-1, network_tick_rate=30)

else:

    atexit.register(report_game_tick_at_exit)
    atexit.register(save_update_history)

    
    game = Client(server_ip=args.ip, server_port=args.port, network_compression=args.enable_compression)

    game.run(max_tick_rate=120,network_tick_rate=30)