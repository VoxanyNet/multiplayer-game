from fight.gamemodes.test.client import TestClient

game = TestClient(server_ip="voxany.net", server_port=5560, network_compression=True)

game.run(max_tick_rate=-1,network_tick_rate=30)