from werkzeug.security import generate_password_hash


senha_para_teste = 'icloudbz12031994@lF' 
hash_correto = generate_password_hash(senha_para_teste)
print("--- HASH GERADO (copie a linha de baixo) ---")
print(hash_correto)