# LoL Summoner Rating

This script generates a rating for a LoL summoner based on recent solo queue performance.

All matches are scored based on individual and team data, focusing on key metrics.

*Please note: Request failures due to rate limiting are not automatically retried.*

## Requirements

[Python](https://www.python.org) 3.9 or higher

[Pipenv](https://pypi.org/project/pipenv/)

## Installation

```
git clone https://github.com/jwtr/lol-summoner-rating.git
cd lol-summoner-rating
pipenv install
```

## Usage

First you need to add your Riot API key, a summoner name and region to the config, for example:

```
config = {
    "riot_api_key": "YOUR-API-KEY",
    "summoner_region": "euw1",
    "summoner_name": "Odoamne",
}
```

Then run:
```
python3 rate_summoner.py
```

## Testing

The code can be tested by running the following:
```
python3 tests.py
```

## Linting

Lint the code using [Flake8](https://pypi.org/project/flake8/):
```
flake8 rate_summoner.py
```

Use [Black](https://pypi.org/project/black/) to autoformat the code:
```
black --line-length 79 rate_summoner.py
```

## License

[MIT](https://choosealicense.com/licenses/mit/)