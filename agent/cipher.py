import os, json, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# CLAVE COMPARTIDA (Debe ser la misma en el Servidor y en el Agente)
# En producción, usa: AESGCM.generate_key(bit_length=256) codificada en base64
SECRET_KEY_B64 = b"bXktc3VwZXItc2VjcmV0LWMyLWtleS0yNTYtYml0cy0="
SECRET_KEY = base64.b64decode(SECRET_KEY_B64)

def encrypt_data(data_dict: dict) -> dict:
    # 1. Serializar el diccionario a texto JSON
    json_bytes = json.dumps(data_dict).encode('utf-8')

    # 2. Generar un vector de inicialización (Nonce) único de 12 bytes
    nonce = os.urandom(12)

    # 3. Cifrar los datos
    aesgcm = AESGCM(SECRET_KEY)
    ciphertext = aesgcm.encrypt(nonce, json_bytes, None)

    # 4. Empaquetar todo en Base64 para poder enviarlo de forma segura por HTTP
    return {
        "nonce": base64.b64encode(nonce).decode('utf-8'),
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8')
    }

def decrypt_data(encrypted_dict: dict) -> dict:
    try:
        # 1. Decodificar los strings Base64 a bytes crudos
        nonce = base64.b64decode(encrypted_dict["nonce"])
        ciphertext = base64.b64decode(encrypted_dict["ciphertext"])

        # 2. Descifrar usando la clave secreta compartida
        aesgcm = AESGCM(SECRET_KEY)
        decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)

        # 3. Reconstruir el diccionario original
        return json.loads(decrypted_bytes.decode('utf-8'))
    except Exception as e:
        print(f"[!] Error de descifrado (¿Clave incorrecta / Manipulación?): {e}")
        return {"error": "Decryption failed"}