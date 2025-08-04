#!/usr/bin/python3.9
import sys
import os

# Obter o diretório atual do script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Adicionar o diretório frontend ao path
frontend_path = os.path.join(current_dir, 'frontend')
if frontend_path not in sys.path:
    sys.path.insert(0, frontend_path)

# Também adicionar o diretório atual ao path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Debug: imprimir os paths para verificar
print(f"Current directory: {current_dir}")
print(f"Frontend path: {frontend_path}")
print(f"Python path: {sys.path}")

# Importar a aplicação Flask
try:
    from app import app as application
    print("Successfully imported app")
except ImportError as e:
    print(f"Import error: {e}")
    # Tentar importar diretamente se estiver no diretório frontend
    try:
        sys.path.insert(0, os.path.join(current_dir, 'frontend'))
        from app import app as application
        print("Successfully imported app from frontend directory")
    except ImportError as e2:
        print(f"Second import error: {e2}")
        raise

if __name__ == "__main__":
    application.run() 