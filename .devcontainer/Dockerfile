FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

#COPY requirements.in /tmp/requirements.in
COPY requirements.txt /tmp/requirements.txt
USER vscode
ENV PATH=/home/vscode/.local/bin:$PATH

RUN pip install --user -r /tmp/requirements.txt

EXPOSE 10000
