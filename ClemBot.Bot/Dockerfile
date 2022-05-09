# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10.4-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Set up and activate virtual environment
ENV VIRTUAL_ENV "/venv"

RUN apt-get update && apt-get install -y git

RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

# Install pip requirements
ADD requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /ClemBot.Bot
ADD . /ClemBot.Bot


# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python","-m", "bot"]
