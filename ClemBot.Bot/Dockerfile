# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y git

# Install poetry
RUN python -m pip install poetry

# Install dependencies with Poetry
WORKDIR /ClemBot.Bot
ADD pyproject.toml .
ADD poetry.lock .

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev --no-interaction

ADD . /ClemBot.Bot

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["poetry", "run", "python3", "-m", "bot"]
