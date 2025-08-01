# server.py

from typing import List, Tuple, Optional, Dict, Union, Callable
import numpy as np
import flwr as fl
from flwr.server import ServerConfig, ServerApp, ServerAppComponents
from flwr.server.strategy import Strategy
from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.common import (
    Parameters, FitIns, FitRes, EvaluateIns, EvaluateRes, Scalar,
    parameters_to_ndarrays, ndarrays_to_parameters, Context
)
import time

from config import NUM_CLIENTS, MIN_NUM_CLIENTS, NUM_ROUNDS
from cipher import SubstitutionCipher

cipher = SubstitutionCipher(seed=42)

# ============================================================================
# AGGREGATION FUNCTIONS WITH TIMING
# ============================================================================

def aggregate_failed_terms(results):
    aggregation_start = time.time()
    term_counter = {}

    for _, fit_res in results:
        # Properly decode parameters
        arrays = parameters_to_ndarrays(fit_res.parameters)
        if not arrays:
            continue

        param_array = arrays[0]
        terms = param_array.tobytes().decode("utf-8").split("\n")
        print('=================BEFORE DECRYPTION==================')
        print(terms)
        print('=================AFTER DECRYPTION==================')
        decrypted_terms = cipher.decrypt_term_list(terms)
        print(decrypted_terms)

        for term in decrypted_terms:
            if term:
                term_counter[term] = term_counter.get(term, 0) + 1

    aggregation_end = time.time()
    aggregation_time = aggregation_end - aggregation_start
    
    print(f"🔧 Server aggregation completed in {aggregation_time:.3f}s")
    
    return term_counter, aggregation_time


def convert_scalar_to_FlowerParameters(aggregated_value: float) -> Parameters:
    """Convert aggregated values (NumPy array) back to Flower parameters"""
    results_array = np.array([aggregated_value])
    return ndarrays_to_parameters([results_array])

# ============================================================================
# FEDERATED ANALYTICS STRATEGY WITH TIMING
# ============================================================================

class FedAnalytics(Strategy):
    """Custom strategy for federated analytics with timing"""
    
    def __init__(self):
        super().__init__()
        self.round_start_times = {}  # Track when each round starts

    def initialize_parameters(self, client_manager: Optional[ClientManager] = None) -> Optional[Parameters]:
        """Initialize global parameters (none needed for analytics)"""
        return None

    def configure_fit(self, server_round: int, parameters: Parameters, client_manager: ClientManager
                      ) -> List[Tuple[ClientProxy, FitIns]]:
        """Configure clients for the fit round"""
        
        # Start timing this round
        round_start = time.time()
        self.round_start_times[server_round] = round_start
        print(f"\n🚀 Round {server_round} started at {time.strftime('%H:%M:%S')}")
        
        config = {}
        fit_ins = FitIns(parameters, config)
        clients = client_manager.sample(num_clients=NUM_CLIENTS, min_num_clients=MIN_NUM_CLIENTS)
        
        print(f"📡 Configured {len(clients)} clients for round {server_round}")
        return [(client, fit_ins) for client in clients]

    def aggregate_fit(self, server_round, results, failures):
        if not results:
            print("No results received")
            return None, {}

        print(f"\n📥 Server received results from {len(results)} clients")
        
        client_times = []
        weighted_accuracy_sum = 0.0
        total_samples = 0
        for _, fit_res in results:
            client_time = fit_res.metrics.get('client_processing_time', 0)
            client_times.append(client_time)

            accuracy = fit_res.metrics.get("accuracy", 0.0)
            num_samples = fit_res.num_examples
            weighted_accuracy_sum += accuracy * num_samples
            total_samples += num_samples
        
        avg_client_time = sum(client_times) / len(client_times) if client_times else 0
        avg_accuracy = weighted_accuracy_sum / total_samples if total_samples > 0 else None
        
        # Time the server aggregation
        metrics, server_aggregation_time = aggregate_failed_terms(results)
        
        # Calculate total round time
        round_start = self.round_start_times.get(server_round, time.time())
        round_end = time.time()
        total_round_time = round_end - round_start
        
        # Calculate communication time
        communication_time = total_round_time - avg_client_time - server_aggregation_time
        
        # Print timing breakdown
        print(f"\n⏱️ TIMING BREAKDOWN - Round {server_round}")
        print(f"   Total round time:        {total_round_time:.3f}s")
        print(f"   Average client time:     {avg_client_time:.3f}s")
        print(f"   Server aggregation:      {server_aggregation_time:.3f}s")
        print(f"   Communication overhead:  {communication_time:.3f}s")
        print(f"   Communication %:         {(communication_time/total_round_time)*100:.1f}%")
        
        if avg_accuracy is not None:
            print(f"weighted accuracy: {avg_accuracy:.4f}")

        # Calculate scalability metrics
        # if len(results) > 0:
        #     client_throughput = len(results) / server_aggregation_time
        #     print(f"   Server throughput:       {client_throughput:.2f} clients/second")
        
        parameters = None
        returned_metrics = metrics.copy()  # failed terms count dictionary
        returned_metrics['weighted_average_accuracy'] = avg_accuracy if avg_accuracy is not None else 999.0

        
        return parameters, returned_metrics

    # Strategy parent class methods have @abstract decorators meaning you need all the methods specified in it, in the ones I dont use I just pass them
    def configure_evaluate(self, server_round: int, parameters: Parameters, client_manager: ClientManager
                        ) -> List[Tuple[ClientProxy, EvaluateIns]]:
        """Configure clients for evaluation (not used in FA)"""
        pass

    def evaluate(self, server_round: int, parameters: Parameters) -> Optional[Tuple[float, Dict[str, Scalar]]]:
        """Evaluate the aggregated parameters (not used in FA)"""
        pass

    def aggregate_evaluate(self, server_round: int, results: List[Tuple[ClientProxy, EvaluateRes]], 
                           failures: List[Union[Tuple[ClientProxy, EvaluateRes], BaseException]]
                           ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        """Aggregate evaluation results (not used in FA)"""
        pass

# ============================================================================
# SERVER APP CONFIGURATION
# ============================================================================

def create_server_config(context: Context) -> ServerAppComponents:
    """Construct components that set the ServerApp behaviour"""
    strategy = FedAnalytics()
    config = ServerConfig(num_rounds=NUM_ROUNDS)
    return ServerAppComponents(strategy=strategy, config=config)

# Create the ServerApp (modern approach)
server = ServerApp(server_fn=create_server_config)

# ============================================================================
# FOR RUNNING server.py (legacy)
# ============================================================================

# Legacy support for direct execution
if __name__ == "__main__":
    print(f"Starting federated analytics server with {NUM_CLIENTS} clients for {NUM_ROUNDS} rounds")
    
    # Use the legacy start_server for direct execution
    fl.server.start_server(
        server_address='127.0.0.1:8080',
        config=ServerConfig(num_rounds=NUM_ROUNDS),
        strategy=FedAnalytics()
    )