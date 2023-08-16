from fight.gamemodes.ragdoll.client import RagdollClient

game = RagdollClient(server_ip="voxany.net", server_port=25580, network_compression=True)

game.run(max_tick_rate=-1,network_tick_rate=60)