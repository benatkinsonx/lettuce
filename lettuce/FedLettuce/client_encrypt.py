# client.py

from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
from datasets import Dataset
from flwr_datasets.partitioner import IidPartitioner
import flwr as fl
from flwr.client import ClientApp, NumPyClient
from flwr.common import Context, ndarrays_to_parameters, parameters_to_ndarrays
import hashlib
import os
import time

from config import NUM_CLIENTS
from groundtruth_checking import ground_truth_checker
from cipher import SubstitutionCipher

# ============================================================================
# DATA LOADING & PARTITIONING
# ============================================================================

def load_clientdata(client_id: int, data_dir: str = "./FedLettuce/data/clientdata"):
    clientdata_file = f'client{client_id}_data.csv'
    clientdata_path = os.path.join(data_dir, clientdata_file)
    client_df = pd.read_csv(clientdata_path)
    print(f'Client {client_id} loaded {len(client_df)} terms from {clientdata_path}')
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

    def fit(self, parameters, config):
        client_start = time.time()
        # Load the partitioned dataset for this client
        partition_df = load_clientdata(self.client_id)
        # Example: identify incorrect terms (replace this with your logic)
        wrongterms = ground_truth_checker(partition_df)
        print(f"Client {self.client_id} wrong terms: {wrongterms}")
        
        cipher = SubstitutionCipher(seed=42)
        encrypted_wrongterms = cipher.encrypt_term_list(wrongterms)

        if len(encrypted_wrongterms) == 0:
            byte_data = b""  # No terms to send
        else:
            joined_terms = "\n".join(encrypted_wrongterms)
            byte_data = joined_terms.encode("utf-8")

        # Convert bytes to uint8 numpy array
        param_array = np.frombuffer(byte_data, dtype=np.uint8)

        client_end = time.time()
        # test

        return ([param_array], len(encrypted_wrongterms), {})




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