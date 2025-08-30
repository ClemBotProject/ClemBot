# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.13-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y git

# Install uv
RUN python -m pip install uv

# Install dependencies with uv
WORKDIR /ClemBot.Bot
ADD pyproject.toml .
ADD uv.lock .

RUN uv sync --no-dev

ADD . /ClemBot.Bot

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["uv", "run", "python", "-m", "bot"]
