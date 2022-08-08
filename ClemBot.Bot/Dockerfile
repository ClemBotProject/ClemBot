# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1


ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1

RUN apt-get update && apt-get install -y git

# Install poetry
RUN python -m pip install poetry

# Install dependencies with Poetry
ADD pyproject.toml .
ADD poetry.lock .
RUN python -m poetry install --no-dev

WORKDIR /ClemBot.Bot
ADD . /ClemBot.Bot

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "-m", "poetry", "run", "python3", "-m", "bot"]
