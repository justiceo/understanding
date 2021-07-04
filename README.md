# Question Generator

## Getting Started
1. Install (Docker Desktop)[https://docs.docker.com/desktop/] - This installs docker engine, docker compose (and other things).
2. Run `docker-compose up`
3. Navigate to `localhost:9200/url=https://en.wikipedia.org/wiki/Drake_(musician)`

## Development
1. Download and install latest python3 (min is 3.9) - https://www.python.org/downloads/
2. Install app dependencies `python3 -m pip install -r requirements.txt`
3. Run sanity tests `pytest`.
4. Start the server `python3 run.py`