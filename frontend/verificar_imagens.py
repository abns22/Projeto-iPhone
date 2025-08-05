#!/usr/bin/env python3
"""
Script para verificar se as imagens estão sendo encontradas corretamente
"""
import os
import mysql.connector

def get_db_connection():
    """Conecta ao banco de dados MySQL"""
    try:
        conn = mysql.connector.connect(
            database='abns22$default',
            user='abns22',
            password='icloudbz12031994@lF',
            host='abns22.mysql.pythonanywhere-services.com',
            port=3306,
            ssl_disabled=False,
            ssl_verify_cert=False,
            ssl_verify_identity=False
        )
        return conn
    except mysql.connector.Error as e:
        print(f"ERRO DE CONEXÃO COM O MYSQL: {e}")
        return None

def verificar_imagens():
    """Verifica se as imagens existem no sistema de arquivos"""
    print("=== VERIFICAÇÃO DE IMAGENS ===")
    
    # Caminho das imagens
    images_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    print(f"Diretório de imagens: {images_dir}")
    
    if not os.path.exists(images_dir):
        print("❌ Diretório de imagens não existe!")
        return
    
    print(f"✅ Diretório de imagens existe")
    
    # Listar arquivos de imagem
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"📁 Encontradas {len(image_files)} imagens no diretório")
    
    # Verificar algumas imagens específicas
    imagens_teste = [
        'ip11branco.jpg',
        'ip11prodourado.png',
        'ip12miniazul.png',
        'ip12preto.png'
    ]
    
    for img in imagens_teste:
        img_path = os.path.join(images_dir, img)
        if os.path.exists(img_path):
            print(f"✅ {img} - EXISTE")
        else:
            print(f"❌ {img} - NÃO EXISTE")

def verificar_banco_dados():
    """Verifica os caminhos das imagens no banco de dados"""
    print("\n=== VERIFICAÇÃO DO BANCO DE DADOS ===")
    
    conn = get_db_connection()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados")
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Verificar modelos
        cursor.execute("SELECT id, nome_modelo, imagem_padrao_url FROM modelos_iphone LIMIT 5")
        modelos = cursor.fetchall()
        
        print(f"📊 Encontrados {len(modelos)} modelos no banco:")
        for modelo in modelos:
            print(f"  - {modelo['nome_modelo']}: {modelo['imagem_padrao_url']}")
        
        # Verificar cores
        cursor.execute("SELECT modelo_id, cor_id, imagem_url FROM modelos_cores LIMIT 5")
        cores = cursor.fetchall()
        
        print(f"\n📊 Encontradas {len(cores)} cores no banco:")
        for cor in cores:
            print(f"  - Modelo {cor['modelo_id']}, Cor {cor['cor_id']}: {cor['imagem_url']}")
            
    except mysql.connector.Error as e:
        print(f"❌ Erro ao consultar banco de dados: {e}")
    finally:
        if conn:
            conn.close()

def verificar_urls():
    """Verifica se as URLs das imagens estão corretas"""
    print("\n=== VERIFICAÇÃO DE URLs ===")
    
    # Simular URLs do Flask
    from flask import url_for
    
    # URLs de exemplo
    urls_teste = [
        'images/ip11branco.jpg',
        'images/ip11prodourado.png',
        'images/ip12miniazul.png'
    ]
    
    for url in urls_teste:
        print(f"📷 URL: {url}")
        # Verificar se o arquivo existe
        img_path = os.path.join(os.path.dirname(__file__), 'static', url)
        if os.path.exists(img_path):
            print(f"  ✅ Arquivo existe: {img_path}")
        else:
            print(f"  ❌ Arquivo não existe: {img_path}")

if __name__ == "__main__":
    verificar_imagens()
    verificar_banco_dados()
    verificar_urls() 