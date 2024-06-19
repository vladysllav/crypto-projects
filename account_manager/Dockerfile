FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY pyproject.toml /code/

# Updating and installing necessary packages
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Add local non-root user to avoid issue with files
ARG USERNAME=code
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash

# Poetry installation and basic dependencies
RUN pip install --upgrade pip setuptools \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install #--no-dev

COPY . /code/

# Select internal user
USER code