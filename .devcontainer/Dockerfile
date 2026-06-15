FROM mcr.microsoft.com/devcontainers/python:latest

RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io docker-cli \
    && rm -rf /var/lib/apt/lists/*
