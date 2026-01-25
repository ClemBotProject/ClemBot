FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install dependencies with uv
WORKDIR /ClemBot.Bot
ADD pyproject.toml .
ADD uv.lock .

RUN uv sync --locked --no-install-project --no-dev

ADD . /ClemBot.Bot

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["uv", "run", "python", "-m", "bot"]
