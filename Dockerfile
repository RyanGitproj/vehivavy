FROM python:3.10-slim

WORKDIR /app
# Copier les dossiers de code source
COPY . /app

RUN pip install -r requirements.txt