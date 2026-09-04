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
