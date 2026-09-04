# 🌌 NovaC2

**NovaC2** es un prototipo de framework **Command & Control (C2)** asíncrono y modular, diseñado desde cero en Python con fines educativos, de investigación y entrenamiento en entornos de laboratorio controlados (*Red Team vs. Blue Team*). 

Este proyecto simula la arquitectura de post-explotación de un atacante avanzado, implementando una interfaz gráfica moderna inspirada en *Starkiller*, endpoints API robustos y un canal de comunicación completamente protegido frente a análisis de red básicos.

---

## 🚀 Características Clave

*   **Arquitectura C2 Asíncrona:** Basada en **FastAPI**, el servidor gestiona múltiples agentes en memoria concurrente sin bloquear el hilo de ejecución principal.
*   **Interfaz Gráfica (GUI) Avanzada:** Diseñada con **NiceGUI**, ofrece un panel de control intuitivo para la administración de *Listeners*, generación de *Stagers* en tiempo real e interacción directa con terminales.
*   **Mecanismo de Beaconing HTTP:** El agente (Implant) interactúa de forma pasiva mediante intervalos de balizamiento (*beacons*), imitando el comportamiento de amenazas persistentes reales para evadir conexiones TCP estáticas.
*   **Criptografía Autenticada (AEAD):** Canal de comunicación cifrado de extremo a extremo utilizando **AES-256-GCM** a través de la librería `cryptography`. Cada paquete incluye un Nonce único aleatorio y verificación de integridad para evitar la manipulación o la inyección de tráfico por parte de analistas defensivos.
*   **Ejecución Nativa Multiplataforma:** El agente captura tanto la salida estándar (`stdout`) como los flujos de error (`stderr`) del sistema operativo objetivo de manera resiliente.

---

## 🛡️ Descargo de Responsabilidad (Disclaimer)

Este software ha sido desarrollado exclusivamente con **fines educativos y de hacking ético**. Su objetivo es ayudar a estudiantes y profesionales de la ciberseguridad a comprender el funcionamiento interno de las herramientas de Comando y Control, así como los artefactos y firmas que dejan en la red y los endpoints. 

El autor no se hace responsable del mal uso, daños o actividades ilícitas realizadas con esta herramienta. Su uso en redes e infraestructuras sin una autorización previa por escrito está estrictamente prohibido.

---

## 📦 Instalación y Despliegue

Sigue estos pasos para montar el entorno de laboratorio y poner en marcha el framework. Se recomienda utilizar un entorno virtual de Python (`venv`) para aislar las dependencias.

### 1. Clonar el repositorio y preparar el entorno
```bash
# Clonar el proyecto
git clone https://github.com
cd tu-repositorio-c2

# Crear un entorno virtual
python -bin -m venv venv

# Activar el entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
.\venv\Scripts\activate

# Instalar todas las dependencias requeridas
pip install -r requirements.txt
```

### 2. Iniciar el Servidor C2 (Handler)
Una vez instaladas las dependencias, despliega el panel de control. El servidor web e interfaz gráfica se levantarán automáticamente.
```bash
cd server
python c2_server.py
```
*   **Acceso a la GUI:** Abre tu navegador web e ingresa a `http://localhost:8080`. Verás el panel de control estilo *Starkiller* completamente operativo.

### 3. Ejecutar el Agente (Implant) en la máquina objetivo
Para simular el compromiso y la ejecución del agente en el laboratorio, abre una nueva terminal (asegúrate de que el script de cifrado compartido esté en la misma carpeta del agente si trabajas en directorios separados):
```bash
cd agent
python implant.py
```

Al ejecutarse, el agente recopilará la información del sistema (Hostname, Usuario, Sistema Operativo e IP interna) e iniciará el ciclo de *beaconing* cada 5 segundos. Recibirás una notificación visual en tiempo real en la interfaz web del servidor confirmando la nueva conexión.

---

## 🛠️ Uso del Framework

1.  **Monitoreo:** Dirígete a la pestaña **Dashboard** o **Agents** en el panel lateral para verificar el estado de los implantes conectados.
2.  **Interacción:** En la sección **Agents**, haz clic en el botón del extremo derecho (icono de terminal) de cualquier agente activo para abrir la consola de interacción dedicada.
3.  **Ejecución:** Escribe cualquier comando nativo del sistema operativo víctima (ej. `whoami`, `ipconfig`, `ls`) en el cuadro de texto inferior y presiona *Enter*. La orden se encolará cifrada, el agente la recogerá en su siguiente *beacon*, la ejecutará y te devolverá el output de forma segura a la pantalla.
