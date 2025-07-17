# client.py

from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
from datasets import Dataset
from flwr_datasets.partitioner import IidPartitioner
import flwr as fl
from flwr.client import ClientApp, NumPyClient
from flwr.common import Context
import hashlib
import os

from config import NUM_CLIENTS

# ============================================================================
# DATA LOADING & PARTITIONING
# ============================================================================

def load_clientdata(client_id: int, data_dir: str = "./data/clientdata"):
    clientdata_file = f'client{client_id}_data.csv'
    clientdata_path = os.join(data_dir, clientdata_file)
    client_df = pd.read_csv(clientdata_path)
    print(f'Client ID: {client_id}, loaded {len(client_df)} instances from {clientdata_path}')
    return client_df

# ============================================================================
# COMPUTATION: RUN LETTUCE CLI (replaces where I wrote the mean age computation)
# ============================================================================



# ============================================================================
# FLOWER CLIENT IMPLEMENTATION
# ============================================================================

class FlowerClient(NumPyClient):
    """Flower client for federated analytics"""
    
    def __init__(self, client_id: int):
        self.client_id = client_id

    # no diff priv
    # def fit(self, parameters, config):
    #     partition_df = load_datasets(df, num_partitions=NUM_CLIENTS, client_id=self.client_id)
    #     print(f"Client {self.client_id} dataset size: {len(partition_df)}")
    #     print(f"First 5 patient IDs: {partition_df.index[:5].tolist()}")
    #     print(f"Mean age: {partition_df['age'].mean()}")
        
    #     partition_mean = compute_mean(partition_df, 'age')

    #     summarystat = [np.array([partition_mean])]
    #     num_examples = len(partition_df)
    #     metrics = {}
    #     return (summarystat, num_examples, metrics)

    # yes diff priv
    def fit(self, parameters, config):
        partition_df = load_datasets(df, num_partitions=NUM_CLIENTS, client_id=self.client_id)
        partition_mean = compute_mean(partition_df, 'age')
        
        # Add local differential privacy
        epsilon = config.get('epsilon', 10.0)
        sensitivity = 60.0 / len(partition_df)  # age range / partition size
        noise = np.random.laplace(0, sensitivity / epsilon)
        noisy_mean = partition_mean + noise
        
        summarystat = [np.array([noisy_mean])]
        return (summarystat, len(partition_df), {})
        
# ============================================================================
# CLIENT APP CONFIGURATION
# ============================================================================

_node_to_client_mapping = {}

# def create_client(context: Context) -> fl.client.Client:
#     global _node_to_client_mapping
    
#     if context.node_id not in _node_to_client_mapping:
#         # Assign next available client ID
#         _node_to_client_mapping[context.node_id] = len(_node_to_client_mapping) % NUM_CLIENTS
    
#     client_id = _node_to_client_mapping[context.node_id]
#     print(f"DEBUG: Node {context.node_id} -> Client ID {client_id} (deterministic)")
    
#     return FlowerClient(client_id=client_id).to_client()

def client_app(context: Context) -> fl.client.Client:
    """Construct a Client that will be run in a ClientApp."""
    
    # Use Flower's node_config approach for deterministic partition assignment
    partition_id = context.node_config.get("partition-id", 0)
    num_partitions = context.node_config.get("num-partitions", NUM_CLIENTS)
    
    print(f"DEBUG: Using partition_id={partition_id} from node_config")
    
    return FlowerClient(client_id=partition_id).to_client()

# Create the ClientApp (modern approach)
client = ClientApp(client_fn=client_app)

# ============================================================================
# FOR RUNNING client.py (legacy)
# ============================================================================

# Legacy support for direct execution
if __name__ == "__main__":
    client_id = int(os.getenv('CLIENT_ID', '0'))
    
    # Use the legacy start_client for direct execution
    fl.client.start_client(
        server_address="127.0.0.1:8080",
        client=FlowerClient(client_id=client_id).to_client(),
    )