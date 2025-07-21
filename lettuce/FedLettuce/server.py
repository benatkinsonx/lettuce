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

from config import NUM_CLIENTS, MIN_NUM_CLIENTS, NUM_ROUNDS

# ============================================================================
# AGGREGATION FUNCTIONS
# ============================================================================

def aggregate_failed_terms(results):
    term_counter = {}

    for _, fit_res in results:
        # Properly decode parameters
        arrays = parameters_to_ndarrays(fit_res.parameters)
        if not arrays:
            continue

        param_array = arrays[0]
        terms = param_array.tobytes().decode("utf-8").split("\n")

        for term in terms:
            if term:
                term_counter[term] = term_counter.get(term, 0) + 1

    return term_counter


def convert_scalar_to_FlowerParameters(aggregated_value: float) -> Parameters:
    """Convert aggregated values (NumPy array) back to Flower parameters"""
    results_array = np.array([aggregated_value])
    return ndarrays_to_parameters([results_array])

# ============================================================================
# FEDERATED ANALYTICS STRATEGY
# ============================================================================

class FedAnalytics(Strategy):
    """Custom strategy for federated analytics on NHS dataset"""
    
    def __init__(self):
        super().__init__()

    def initialize_parameters(self, client_manager: Optional[ClientManager] = None) -> Optional[Parameters]:
        """Initialize global parameters (none needed for analytics)"""
        return None

    def configure_fit(self, server_round: int, parameters: Parameters, client_manager: ClientManager
                      ) -> List[Tuple[ClientProxy, FitIns]]:
        """Configure clients for the fit round"""
        config = {}
        fit_ins = FitIns(parameters, config)
        clients = client_manager.sample(num_clients=NUM_CLIENTS, min_num_clients=MIN_NUM_CLIENTS)
        return [(client, fit_ins) for client in clients]

    def aggregate_fit(self, server_round, results, failures):
        if not results:
            print("No results received")
            return None, {}

        # Gather all failed terms
        failed_terms = aggregate_failed_terms(results)
        print(f"❌ Aggregated failed terms from round {server_round}: {failed_terms}")

        # Join all failed terms into one string separated by newline
        failed_terms_str = "\n".join(failed_terms.keys())
        
        # Encode the string into bytes
        failed_terms_bytes = failed_terms_str.encode("utf-8")
        
        # Convert bytes to numpy uint8 array (numeric, no objects)
        failed_terms_np = np.frombuffer(failed_terms_bytes, dtype=np.uint8)
        
        # Convert to Flower Parameters
        parameters = ndarrays_to_parameters([failed_terms_np])
        
        return parameters, {"num_failed_terms": len(failed_terms)}


    def evaluate(self, server_round: int, parameters: Parameters) -> Optional[Tuple[float, Dict[str, Scalar]]]:
        """Evaluate the aggregated parameters"""
        return None
        
        agg_scalar = [arr.item() for arr in parameters_to_ndarrays(parameters)]
        return 0, {"Aggregated mean age": agg_scalar}

    def configure_evaluate(self, server_round: int, parameters: Parameters, client_manager: ClientManager
                           ) -> List[Tuple[ClientProxy, EvaluateIns]]:
        """Configure clients for evaluation (not used in analytics)"""
        pass

    def aggregate_evaluate(self, server_round: int, results: List[Tuple[ClientProxy, EvaluateRes]], 
                           failures: List[Union[Tuple[ClientProxy, EvaluateRes], BaseException]]
                           ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        """Aggregate evaluation results (not used in analytics)"""
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