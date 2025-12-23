from passlib.context import CryptContext

# Configuração do Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

senha_plana = "Ledax@hub"
senha_hash = pwd_context.hash(senha_plana)

print("\n--- COPIE O CÓDIGO ABAIXO ---")
print(senha_hash)
print("-----------------------------\n")