# 🔄 Sync Bridge & Firebase Hosting

**Módulo:** `app/services/firebase_sync.py`  
**Hosting URL:** [`https://videopro-studio.web.app`](https://videopro-studio.web.app)

---

## 1. Funcionamiento del Sync Bridge
VideoPro sincroniza automáticamente en segundo plano cualquier cambio en la interfaz de Streamlit hacia Firebase Firestore para evitar cuellos de botella en la UI:
- **`save_settings_to_firebase_async()`**: Guarda `global_config` y `providers_registry` de forma no bloqueante.
- **`backup_project_to_firebase_async(project)`**: Respalda el estado completo del proyecto al generar o editar escenas.
- **`fetch_all_projects_from_firebase()`**: Carga la lista completa de proyectos al abrir la vista `📁 Proyectos`.
