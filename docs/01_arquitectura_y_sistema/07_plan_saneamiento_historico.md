# PLAN DE LIMPIEZA Y ESTABILIZACIÓN — VIDEOPRO STUDIO

---

## 1. OBJETIVO DE LA LIMPIEZA
Eliminar código muerto, copias de seguridad residuales, scripts obsoletos y servicios en bucle de fallo, garantizando que el repositorio quede en un estado limpio, seguro y reproducible sin alterar ninguna funcionalidad activa del generador de vídeo.

---

## 2. FASES DE LIMPIEZA Y VERIFICACIÓN

### FASE 1: Resolución de Conflictos de Runtime & DevOps
- [x] Detener el servicio `videopro-v2.service` en systemd que genera bucle de reinicio infinito en puerto 7001.
- [x] Deshabilitar el unit file antiguo para liberar CPU y recursos del sistema.

### FASE 2: Eliminación de Archivos Basura y Temporales
- [x] Eliminar `webui/Main.py.bak` (copia de seguridad huérfana).
- [x] Eliminar `webui/Main.py.monolith.bak` (copia de seguridad huérfana).
- [x] Eliminar `videopro_7001.log` y `videopro_spa_7001.log` de la raíz del repositorio.
- [x] Actualizar `.gitignore` para ignorar de forma estricta:
  - `*.log`
  - `*.bak`
  - `*.tmp`
  - `storage/tasks/`
  - `storage/renders/`

### FASE 3: Aislamiento Seguro de Código Legacy
- [x] Mover `server/` y `web/` a un directorio aislado `legacy/` o eliminarlos una vez verificado que `app/asgi.py` y `webui/Main.py` son los únicos consumidores activos.
- [x] Eliminar `run_spa_7001.sh` (script del prototipo antiguo).

### FASE 4: Validación Integral de No Regresión
- [x] Comprobar arranque de FastAPI en puerto 8080 (`/ping`, `/docs`, `/api/v1/matrix/data`, `/api/v1/pipeline/graph`).
- [x] Comprobar arranque de Streamlit en puerto 7001 (`webui/Main.py`).
- [x] Validar sincronización con Firebase Firestore.
- [x] Ejecutar suite de pruebas de almacenamiento y providers.
