# VIDEOPRO — MAPA DE PUERTOS Y RUNTIME DE SERVICIOS (RUNTIME_MAP.md)

**Versión:** 1.0.0 — Canónica  
**Estado:** `CURRENT / SINGLE SOURCE OF TRUTH`  
**Última Actualización:** Agosto 2026

Este documento es la **única fuente de verdad** para los puertos, hosts, protocolos y estados de todos los servicios asociados a VideoPro.

---

## 🗺️ TABLA DE PUERTOS Y SERVICIOS ACTIVOS

| Servicio | Puerto | Host / Bind | Protocolo | Propósito | Entorno | Proceso / Unit | Estado Real |
| :--- | :---: | :---: | :---: | :--- | :--- | :--- | :---: |
| **VideoPro Studio Frontend** | **`7001`** | `0.0.0.0` | HTTP / WS | Interfaz Web Principal (Streamlit) | Local VPS | `moneyprinter-webui.service` | 🟢 **ONLINE** |
| **VideoPro Backend API** | **`8080`** | `127.0.0.1` | HTTP (REST) | API FastAPI, Orquestador y Endpoints | Local VPS | `moneyprinter-api.service` | 🟢 **ONLINE** |
| **Antigravity Bridge** | **`8742`** | `0.0.0.0` | HTTP (OpenAI) | Inferencia LLM Local (Gemini 3.7 Flash) | Local VPS | `hermes-antigravity-provider` | 🟢 **ONLINE** |
| **Ollama Local Engine** | **`11434`** | `127.0.0.1` | HTTP | Inferencia local para modelos open-source | Local VPS | `ollama.service` | 🟢 **ONLINE** |
| **VideoPro Web Portal** | **`3000`** | `0.0.0.0` | HTTP | Portal Web de Visualización | Local VPS | Node.js Process | 🟢 **ONLINE** |
| **Firebase Firestore** | **`443`** | Cloud (GCP) | HTTPS | Base de datos NoSQL para metadatos | Cloud | Google Cloud SDK | 🟢 **ONLINE** |
| **Cloudflare R2 Storage** | **`443`** | Cloud (CF) | HTTPS (S3) | Bóveda de almacenamiento de vídeos y fotos | Cloud | S3 Boto3 Client | 🟢 **ONLINE** |
| **ComfyUI Server** | **`8188`** | `127.0.0.1` | HTTP / WS | Runtime externo de grafos ComfyUI | Externo | N/A | ⚪ **PLANNED** |
| **RunPod Serverless** | **`443`** | `api.runpod.ai`| HTTPS | Ejecución remota de workers GPU | Cloud | RunPod API | ⚪ **PLANNED** |

---

## 🔒 POLÍTICA DE PUERTOS Y AISLAMIENTO

1. **Frontend (Puerto 7001)**:
   - Expuesto para acceso de usuario y navegación en navegador.
   - Ejecuta `webui/Main.py`.
2. **Backend API (Puerto 8080)**:
   - Vinculado a `127.0.0.1:8080` o enrutado mediante reverse proxy.
   - Documentación Swagger interactiva en `http://127.0.0.1:8080/docs`.
3. **Bridge Local (Puerto 8742)**:
   - Proveedor de inferencia compatible con OpenAI (`http://127.0.0.1:8742/v1`).
4. **Prohibición de Puertos Fantasma**:
   - Queda terminantemente prohibido referenciar puertos no existentes o antiguos (como `8501`, `7895`, `9000`) en la documentación de producción.
