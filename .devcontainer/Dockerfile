##########################
### dev
##########################
ARG BASE_IMAGE=mcr.microsoft.com/devcontainers/python:3.12
FROM "${BASE_IMAGE}" AS dev

ENV PIP_NO_CACHE_DIR=True

USER root

# Install system dependencies
# - bash-completion for shell completions of invoke

RUN sudo apt-get update && \
  export DEBIAN_FRONTEND=noninteractive && \
  apt-get install -y bash-completion && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

USER vscode

# pipx is already installed in the base devcontainers Python image
RUN pipx install poetry && \
  poetry completions bash >> ~/.bash_completion