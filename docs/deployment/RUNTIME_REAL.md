# RUNTIME & DEPLOYMENT — VIDEOPRO STUDIO

---

## 1. MAPA DE PUERTOS Y SERVICIOS ACTIVOS

```text
┌─────────────────────────────────────────────────────────────┐
│                          VPS HOST                           │
├─────────────┬───────────────────────────┬───────────────────┤
│ Puerto      │ Proceso / Servicio        │ Propósito         │
├─────────────┼───────────────────────────┼───────────────────┤
│ 8080 (TCP)  │ FastAPI Backend (main.py) │ API REST & Engine │
│ 7001 (TCP)  │ Streamlit (webui/Main.py) │ Frontend Visual   │
│ 8742 (TCP)  │ Antigravity CLI Bridge    │ LLM Gemini 3.7 $0 │
│ 6080 / 5900 │ noVNC / X11 Server        │ Desktop Remoto    │
└─────────────┴───────────────────────────┴───────────────────┘
```

---

## 2. SCRIPTS DE ARRANQUE OFICIALES

### 2.1 Backend FastAPI
```bash
# Ejecución directa con uvicorn
/home/ubuntu/MoneyPrinterTurbo/.venv/bin/python main.py
```
- Lee la configuración desde `config.toml` (`listen_host = "127.0.0.1"`, `listen_port = 8080`).
- Documentación Swagger interactiva disponible en: `http://127.0.0.1:8080/docs`.

### 2.2 Frontend Streamlit
```bash
# Script de inicio oficial en puerto 7001
./run_dev_7001.sh
```
- Inicia Streamlit en `0.0.0.0:7001` con recarga en guardado activada (`--server.runOnSave=true`).

---

## 3. SERVICIOS SYSTEMD Y ACCIONES CORRECTIVAS

### 3.1 Corrección de `videopro-v2.service`
- **Problema detectado:** El servicio antiguo ejecutaba `server/videopro_server.py` compitiendo por el puerto `7001`.
- **Configuración corregida recomendada para producción (`/etc/systemd/system/videopro-api.service`):**
```ini
[Unit]
Description=VideoPro Studio FastAPI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/workspace/pro/hermes/10_videopro
ExecStart=/home/ubuntu/MoneyPrinterTurbo/.venv/bin/python main.py
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
