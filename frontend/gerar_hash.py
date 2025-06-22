# gerar_hash.py
from werkzeug.security import generate_password_hash
import getpass

# Pede para você digitar a senha de forma segura, sem mostrá-la na tela
try:
    senha = getpass.getpass("Digite a senha para o seu usuário admin: ")
    senha_confirmacao = getpass.getpass("Confirme a senha: ")

    if senha != senha_confirmacao:
        print("\nAs senhas não coincidem. Abortando.")
    elif not senha:
        print("\nA senha não pode ser vazia. Abortando.")
    else:
        # Gera o hash da senha
        hash_da_senha = generate_password_hash(senha)
        print("\nSeu hash de senha foi gerado com sucesso!")
        print("Copie a linha abaixo e guarde-a para o próximo passo:")
        print("----------------------------------------------------")
        print(hash_da_senha)
        print("----------------------------------------------------")

except Exception as e:
    print(f"Ocorreu um erro: {e}")