FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

# Update apt and install system dependencies
RUN apt-get update && \
    apt-get install -y shellcheck
    # Install Node.js 20.x
#    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
#    apt-get install -y nodejs && \
#    # Install devcontainer CLI globally
#    npm install -g @devcontainers/cli

COPY requirements.in /tmp/requirements.in
USER vscode
ENV PATH=/home/vscode/.local/bin:$PATH

RUN pip install --user -r /tmp/requirements.in

# EXPOSE 5000
