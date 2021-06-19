# Question Generator

## Setup
1. Install (Docker Desktop)[https://docs.docker.com/desktop/] - This installs docker engine, docker compose (and other things).
2. Run `docker-compose up`
3. Install poetry `which poetry || pip3 install poetry`
4. Download and install latest python3 (min is 3.9) - https://www.python.org/downloads/
5. Install project dependencies `poetry install` or `~/.poetry/bin/poetry install` if binary not in $PATH.
6. Run sanity tests `poetry run pytest`.
7. Start program `poetry run python3 run.py`