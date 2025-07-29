#!/usr/bin/python3.9
import sys
import os

# Adicionar o diretório frontend ao path do Python
sys.path.append('/home/abns22/Projeto-iPhone/frontend')

# Importar a aplicação Flask
from app import app as application

if __name__ == "__main__":
    application.run() 