# BenAtkinson FedLettuce

## Setup

- sudo apt update && sudo apt upgrade -y
- sudo add -apt-repository ppa:deadsnakes/ppa
- sudo apt update
- sudo apt install python 3.12 python 3.12-env python 3.12-dev -y
- sudo apt install python3 python3-pip -y
- sudo apt install pipx
- pipx ensure path
 
now open a new terminal window
 
- pipx install uv
- sudo apt install python-is-python3

(cd into where you want the cloned repo to go)

- git clone https://github.com/benatkinsonx/lettuce.git

(if you are doing this for the first time using GitHub)

- git config --global user.name "insert_username"
- git config --global user.email "insert_email"
- code --verbose
- code .
- add .env file in lettuce/lettuce/.env

.env file contents:

DB_HOST=localhost

DB_USER=postgres

DB_PASSWORD=password

DB_NAME=omop

DB_PORT=5432

DB_SCHEMA=public

DB_VECTABLE="embeddings"

DB_VECSIZE=384

- (cd into lettuce/lettuce) uv add "flwr[simulation]" --> this has already been done and is in the pyproject.toml

## How to run FedLettuce

### The steps in making sure everything runs:

1) (cd into lettuce/lettuce) uv run --env-file .env lettuce-cli --informal_names "ibuprofen"
2) uv run python FedLettuce/nonflower-attempts/running_lettuce.py
3) uv run python FedLettuce/nonflower-attempts/ground_truth_checker.py
4) (to split the HELIOS test set up) uv run python FedLettuce/data/data_partitioner.py
5) (running the actual FedLettuce implementation) uv run python FedLettuce/simulation.py

# Lettuce
This directory contains the main Lettuce program, an AI assistant for making OMOP mappings.

For detailed instructions follow the [Lettuce docs](https://health-informatics-uon/github.io/lettuce).

## Dependencies
Lettuce now uses `uv` for dependency management. To install `uv` (MacOS / Linux) run: 
```bash 
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Then run the following command: 
```bash
uv sync  --all-extras
```
This command will create a `.venv` folder (if it doesn't already exist) at the root of the project and install the main and developer dependencies. Omit the `--all-extras` flag to install the main package only. It will also re-lock the project by generating a `uv.lock` file. See the [`uv` documentation](https://docs.astral.sh/uv/reference/cli/#uv-sync) for further details.
## Running the CLI
Lettuce has a command-line interface, run it with `uv run lettuce-cli`

## Starting the API
Running `uv run python app.py` will start up the Lettuce API on port 8000
