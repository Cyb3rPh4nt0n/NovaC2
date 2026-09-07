import os, json, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# CLAVE COMPARTIDA (Debe ser la misma en el Servidor y en el Agente)
# En producción, usa: AESGCM.generate_key(bit_length=256) codificada en base64
MASTER_KEY_B64 = b"bXktc3VwZXItc2VjcmV0LWMyLWtleS0yNTYtYml0cy0="
MASTER_KEY = base64.b64decode(MASTER_KEY_B64)

def derive_agent_key(agent_name: str) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,                  # Clave de 256 bits para AES
        salt=b"NovaC2_Crypto_Salt_v1", # Sal estática para dar consistencia
        info=agent_name.encode('utf-8') # El contexto único es el nombre del agente
    )
    return hkdf.derive(MASTER_KEY)

def encrypt_data(data_dict: dict, agent_name: str) -> dict:
    # 1. Serializar el diccionario a bytes
    json_bytes = json.dumps(data_dict).encode('utf-8')

    # 2. Generar un vector de inicialización (Nonce) seguro de 12 bytes
    nonce = os.urandom(12)

    # 3. Derivar la clave específica para este agente
    agent_key = derive_agent_key(agent_name)
    aesgcm = AESGCM(agent_key)

    # 4. Cifrar inyectando el nombre del agente como AAD (Authenticated Associated Data)
    # Esto asegura que este paquete solo sea válido si lo procesa el agente correcto.
    aad = agent_name.encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, json_bytes, aad)

    # 5. Empaquetado Base64 seguro para tránsito web
    return {
        "nonce": base64.b64encode(nonce).decode('utf-8'),
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8')
    }

def decrypt_data(encrypted_dict: dict, agent_name: str) -> dict:
    try:
        # 1. Decodificar estructuras Base64
        nonce = base64.b64decode(encrypted_dict["nonce"])
        ciphertext = base64.b64decode(encrypted_dict["ciphertext"])

        # 2. Reconstruir la clave única del agente
        agent_key = derive_agent_key(agent_name)
        aesgcm = AESGCM(agent_key)

        # 3. Descifrar validando la identidad (AAD)
        aad = agent_name.encode('utf-8')
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, aad)

        # 4. Retornar los datos limpios
        return json.loads(decrypted_bytes.decode('utf-8'))
    except Exception as e:
        # Registros silenciosos en producción para no dar pistas a atacantes en red
        print(f"[!] Error de autenticación/descifrado para {agent_name}: {e}")
        return {"error": "Decryption/Authentication failed"}