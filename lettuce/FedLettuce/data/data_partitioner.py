import pandas as pd
import numpy as np
from pathlib import Path
import shutil

# =============================================================================
# define absolute file paths
# =============================================================================
data_dir = Path(__file__).parent
testset_path = data_dir / 'EU_test_set.csv'
clientdata_path = data_dir / 'clientdata'

# =============================================================================
# deletes existing client data files
# =============================================================================
if clientdata_path.is_dir():
    print('deleting clientdata')
    shutil.rmtree(clientdata_path)

# =============================================================================
# makes new client data folder
# =============================================================================
clientdata_path.mkdir(parents=True, exist_ok=True)

# =============================================================================
# loads in the test set, partitions it and saves it to files within clientdata folder
# =============================================================================
df = pd.read_csv(testset_path)
informal_names = df['input_data'].tolist()

num_clients = 3
partitioned_df = np.array_split(df, num_clients)

for client_id in range(num_clients):
    client_df = partitioned_df[client_id]
    client_csv_path = data_dir / 'clientdata' / f'client{client_id}_data.csv'
    client_df.to_csv(client_csv_path, index=False)


