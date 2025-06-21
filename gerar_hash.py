from werkzeug.security import generate_password_hash

senha_para_teste = 'senha123'  # Escolha a senha que você quer para o seu usuário de teste
hash_correto = generate_password_hash(senha_para_teste)
print("Copie este hash para o seu banco de dados:")
print(hash_correto)