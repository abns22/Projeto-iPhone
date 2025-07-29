#!/usr/bin/python3.9
import sys
import os

# Adicionar o diretório frontend ao path
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
if path not in sys.path:
    sys.path.append(path)

# Importar a aplicação Flask
from app import app as application

if __name__ == "__main__":
    application.run() 