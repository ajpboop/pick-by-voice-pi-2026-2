#!/bin/sh
# Executa o sistema usando o ambiente virtual do projeto
cd "$(dirname "$0")" || exit 1
exec .venv/bin/python main.py
