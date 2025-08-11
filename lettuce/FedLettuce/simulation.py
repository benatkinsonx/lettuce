# simulation.py

# IT WORKS IT WORKS FLOWER WORKS YAYYYY
# update: sometimes flower will say out of memory error --> solution: restart laptop

import flwr as fl
from flwr.simulation import run_simulation
import torch

from config import NUM_CLIENTS

# server and client apps
from server_decrypt import server
from client_encrypt import client


if __name__ == "__main__":
    # print('BA-TIMING-BRANCH')
    # Backend configuration

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {DEVICE}")

    # Backend config with GPU detection (from Flower tutorial)
    backend_config = {"client_resources": {"num_cpus": 1, "num_gpus": 0.0}}

    # if DEVICE == "cuda":
    #     print('DEVICE = CUDA')
    #     total_cpus = 128
    #     total_gpus = 2
        
    #     available_cpus = total_cpus - 4  # Reserve 4 cores for system
    #     gpu_per_client = total_gpus / NUM_CLIENTS
        
    #     backend_config = {
    #         "client_resources": {
    #             "num_cpus": 1.0,
    #             "num_gpus": gpu_per_client
    #         }
    #     }
    # Create client configurations to ensure proper partition assignment
    client_configs = []
    for i in range(NUM_CLIENTS):
        print(f'SIMULATING CLIENT {i}')
        client_configs.append({"client_id": i})
    
    # Run simulation with explicit client configurations
    run_simulation(
        server_app=server,
        client_app=client,
        num_supernodes=NUM_CLIENTS,
        backend_config=backend_config
    )