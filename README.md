# weekly chess digest
**get a weekly slack message with links to your best chess games!**

## How it works
`weekly_digest.py` defines a Prefect flow that runs an engine (like [stockfish](https://github.com/official-stockfish/Stockfish)) in order to calculate [centipawn loss](https://chess.stackexchange.com/questions/26469/average-centipawn-loss) on PGNs and sends the `top_N_games` by this metric to a Slack webhook url as a list of markdown [blocks](https://api.slack.com/block-kit).


## Setup
Requires python 3.10+ and `prefect>=2.7.7`

### Auxilliary resources
- a chess engine (like stockfish) running at some path accessible to your machine, e.g. `opt/homebrew/bin/stockfish`

- [Prefect secret](https://discourse.prefect.io/t/how-to-securely-store-secrets-in-prefect-2-0/1209) called `slack-digest-url` that stores your desired webhook URL (will potentially add NotifBlock in future)

### Setup venv
```bash
# miniconda for example
conda create -n pychess python=3.10 -y
conda activate pychess
pip install -r requirements.txt
```
