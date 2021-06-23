# syntax=docker/dockerfile:1

FROM python:3.9.5

RUN python3 --version

# Install requirements
WORKDIR /code
COPY requirements.txt ./
RUN python3 -m pip install -r requirements.txt

# Copy everything else to docker directory.
COPY . .

# Start application.
CMD ["python3", "src/run.py"]