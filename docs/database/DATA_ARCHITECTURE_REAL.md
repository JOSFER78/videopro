# ARQUITECTURA DE DATOS Y PERSISTENCIA — VIDEOPRO STUDIO

**Proyecto Firebase:** `ayuda-emilio-83261`  
**Base de Datos:** Cloud Firestore `(default)`  
**Almacenamiento Objeto:** Cloudflare R2 (`videpro/videos/`)  
**Almacenamiento Local:** `storage/`

---

## 1. FUENTES DE VERDAD POR ENTIDAD

| Entidad | Fuente de Verdad | Caché / Materialización | Ciclo de Vida | Ownership |
| :--- | :--- | :--- | :--- | :--- |
| **Configuración Global** | Firestore `videopro_settings/global_config` | `config.toml` (Local) | Persistente, modificado por usuario en UI | Admin / Sistema |
| **Matriz de Proveedores** | Firestore `videopro_settings/providers_registry` | `storage/providers_registry.json` | Persistente, modificado al conmutar motores | Sistema |
| **Proveedores Eliminados** | Firestore `videopro_settings/providers_registry` | `storage/deleted_providers.json` | Persistente | Admin |
| **Grafo ComfyUI** | `storage/pipeline_graph.json` | Memoria del Asistente Agéntico | Persistente, mutado por órdenes IA o Canvas | Usuario / Agente |
| **Manifiesto de Tarea** | `storage/tasks/.../script.json` | Firestore (Opcional) | Vinculado al trabajo de render | Job Worker |
| **Clips y Render MP4** | Cloudflare R2 + `storage/tasks/.../` | Memoria temporal | Persistente en R2 / Temporal local | Storage Engine |

---

## 2. ESQUEMAS DE DOCUMENTOS FIRESTORE

### 2.1 Colección: `videopro_settings`
#### Documento: `global_config`
```json
{
  "app_name": "VideoPro Creative Studio",
  "hosting_url": "https://videopro-studio.web.app",
  "updated_at": "2026-08-16T04:48:33.297736",
  "config_json": "{\"llm_provider\": \"Gemini (Google AI Studio)\", \"openai_base_url\": \"http://127.0.0.1:8742/v1\", \"openai_model_name\": \"gemini-3.7-flash-high\", \"video_source\": \"hybrid\", \"s3_endpoint\": \"https://9d248b8b5baed3559e743ef138d25b64.r2.cloudflarestorage.com\", \"s3_bucket\": \"videpro/videos/\", ...}"
}
```

#### Documento: `providers_registry`
```json
{
  "updated_at": "2026-08-16T04:48:34.385469",
  "registry_json": "{ \"nanobanana\": { ... }, \"flux_zerogpu\": { ... }, \"ltx25\": { ... }, \"google_flow\": { ... }, \"vibevoice_serverless\": { ... } }",
  "deleted_providers_json": "[\"anthropic\", \"deepseek\", \"fal_ai\", \"kokoro\", \"wan21\", \"minimax_h3\"]"
}
```

### 2.2 Colección: `videopro_system`
#### Documento: `status`
```json
{
  "app_name": "VideoPro Creative Studio",
  "hosting_url": "https://videopro-studio.web.app",
  "updated_at": "2026-08-16T01:14:00Z"
}
```

---

## 3. POLÍTICA DE SEGURIDAD Y REGLAS DE FIREBASE
Las reglas de seguridad de Firestore para VideoPro protegen el acceso autenticado:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /videopro_settings/{document} {
      allow read, write: if request.auth != null || request.auth.token.firebase.sign_in_provider != null;
    }
    match /videopro_system/{document} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```
