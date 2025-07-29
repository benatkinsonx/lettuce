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

from config import NUM_CLIENTS
from groundtruth_checking import ground_truth_checker

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
    """Flower client that processes all clients sequentially"""
    
    def __init__(self):
        # No specific client_id - we'll process all of them
        pass

    def fit(self, parameters, config):
        all_wrong_terms = []
        
        # Iterate through all clients sequentially
        for client_id in range(NUM_CLIENTS):
            print(f"Processing client {client_id}...")
            
            # Load data for this client
            partition_df = load_clientdata(client_id)
            
            # Process the data
            wrong_terms = ground_truth_checker(partition_df)
            print(f"Client {client_id} wrong terms: {wrong_terms}")
            
            # Collect results
            all_wrong_terms.extend(wrong_terms)
            
            # Optional: add some delay or memory cleanup
            import gc
            gc.collect()
        
        # Convert all results to bytes
        if len(all_wrong_terms) == 0:
            byte_data = b""
        else:
            joined_terms = "\n".join(all_wrong_terms)
            byte_data = joined_terms.encode("utf-8")

        param_array = np.frombuffer(byte_data, dtype=np.uint8)
        return ([param_array], len(all_wrong_terms), {})

def client_app(context: Context) -> fl.client.Client:
    """Single client that processes all data"""
    return FlowerClient().to_client()

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