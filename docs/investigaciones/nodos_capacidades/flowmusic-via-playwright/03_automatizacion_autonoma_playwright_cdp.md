# Automatización Autónoma de Google Flow Music vía Playwright & CDP

## 1. El Desafío: ¿Por qué Flow Music es "Web-Only" y Cómo Resolverlo?

### La Realidad del Ecosistema Google Labs / Flow Music
A diferencia de servicios con APIs REST tradicionales (como OpenAI o ElevenLabs), **Google Flow Music (MusicFX / Lyria 3 Pro)** dentro del ecosistema `labs.google/fx` opera bajo un modelo de consumo estrictamente web:
1. **Autenticación Basada en Sesión Google**: Utiliza cookies HTTPOnly cifradas (`__Secure-3PAPISID`, `HSID`, `SSID`, `SIDCC`) y tokens OAuth vinculados a la cuenta de Google del usuario.
2. **Saldo de Créditos Exclusivo en Frontend**: Los créditos promocionales y de suscripción residen en la plataforma web de Google Labs y se descuentan a través de llamadas internas TrPC/gRPC (`labs.google/fx/api/trpc/...`).
3. **Ausencia de API REST Pública**: No existe un endpoint oficial con `api_key` estándar para consumir estos créditos desde terminal/curl sin una sesión de navegador activa.

### La Solución Óptima: Playwright sobre CDP (Chrome DevTools Protocol)
La mejor y más robusta arquitectura para automatizar este flujo **100% desatendido** (sin intervención humana y sin riesgo de bloqueos de seguridad) consiste en **acoplar Playwright a la sesión activa del navegador en el VPS vía CDP (puerto 9222/9223)**.

---

## 2. Arquitectura del Sistema de Automatización

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             VIDEO PRO PIPELINE                              │
│  (Orquestador CHRONODRIFT, Scene Director, Escaletas Tritemporales)        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Solicita BSO (Prompt, Mood, Hz, BPM)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLOW MUSIC PLAYWRIGHT RUNNER (PYTHON)                    │
│  - app/services/audio/flowmusic_service.py                                  │
│  - scripts/flow_music_playwright_runner.py                                  │
└──────┬───────────────────────────────────────────────────────────────┬──────┘
       │                                                               │
       │ 1. Conexión CDP WebSocket (:9222)                             │ 5. DSP Mastering
       ▼                                                               ▼
┌──────────────────────────────────────┐     ┌────────────────────────────────┐
│   NAVEGADOR VPS (Brave / Chromium)   │     │   AUDIOPHILE DSP PROCESSOR     │
│   - Headless / Xvfb Display :99      │     │   - Pitch Shift 432Hz / 528Hz  │
│   - Perfil Activo Autenticado        │     │   - Crossfeed Meier Binaural   │
│   - URL: labs.google/fx/tools/flow   │     │   - Compresión M/S Dinámica    │
│   - Consume Créditos Web Reales      │     │   - Normalización -14 LUFS     │
└──────────────────┬───────────────────┘     └────────────────┬───────────────┘
                   │                                          │
                   │ 2. Inyecta Prompt & Parámetros           │ 6. Audio Master
                   │ 3. Dispara Generación                    │
                   │ 4. Descarga Blob Audio / Stream          ▼
                   └───────────────────────────► ┌────────────────────────────┐
                                                 │   VIDEO STORAGE MANAGER    │
                                                 │   data/audio/flow_music/   │
                                                 └────────────────────────────┘
```

---

## 3. Comparativa de Métodos de Automatización Web

| Criterio | Método 1: Playwright sobre CDP Activo (:9222) ⭐ **(RECOMENDADO)** | Método 2: Contexto Persistente (`user_data_dir`) | Método 3: Reingeniería de API TrPC / Curl | Método 4: CUA / Desktop Visual Click |
| :--- | :--- | :--- | :--- | :--- |
| **Estabilidad de Sesión** | **100% Máxima**: Reutiliza la sesión autenticada sin reinicios de browser. | **Alta**: Inicia un proceso Chromium nuevo con la carpeta de perfil. | **Baja**: Requiere regenerar tokens CSRF/TrPC y firmas de cabecera. | **Media**: Sensible a cambios de resolución o ventanas tapadas. |
| **Riesgo de CAPTCHA** | **Cero**: Google ve un navegador que ya completó el handshake. | **Bajo**: Puede disparar "Dispositivo nuevo" si cambian flags. | **Alto**: Bloqueo inmediato por Cloudflare/BotGuard de Google. | **Cero**: Simula entradas de hardware. |
| **Velocidad de Petición** | **Alta** (~1-2 seg overhead + tiempo de generación de Flow). | **Media** (~3-5 seg overhead por inicio de binario). | **Ultra Rápida** (milisegundos, pero frágil). | **Lenta** (~5-10 seg por navegación y escaneo visual). |
| **Extracción de Audio** | **Directa**: Captura `expect_download` o lee el `Blob` de memoria en JS. | **Directa**: Captura eventos de descarga nativos. | **Directa**: Stream HTTP. | **Indirecta**: Clics en menús de descarga. |
| **Consumo de Recursos** | **Óptimo**: No duplica instancias de Chromium en memoria RAM. | **Pesado**: Inicia un Chromium completo por lote. | **Mínimo**: Sólo peticiones HTTP. | **Alto**: Xvfb + procesamiento de capturas. |

---

## 4. Estrategia de Selección de Elementos DOM y Triggers

### 1. Detección y Conexión al Navegador Activo
```python
async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    
    # Reutilizar pestaña de Flow Music o crear una nueva
    page = None
    for pg in context.pages:
        if "labs.google" in pg.url and ("music" in pg.url or "flow" in pg.url):
            page = pg
            break
    if not page:
        page = await context.new_page()
        await page.goto("https://labs.google/fx/tools/music-fx", wait_until="domcontentloaded")
```

### 2. Cierre Autónomo de Modales y Banners
```python
modal_selectors = [
    'button:has-text("Aceptar")',
    'button:has-text("Entendido")',
    'button:has-text("Got it")',
    'button:has-text("Continuar")',
    'button[aria-label*="Close"]',
    'button[aria-label*="Cerrar"]'
]
for sel in modal_selectors:
    btn = page.locator(sel).first
    if await btn.count() > 0 and await btn.is_visible():
        await btn.click()
        await page.wait_for_timeout(300)
```

### 3. Inyección Precisa del Prompt y Configuración
```python
# Soportar tanto textarea estándar como contenteditable moderno de Google Labs
prompt_field = page.locator('textarea:visible, div[contenteditable="true"]:visible').first
await prompt_field.click()
await prompt_field.fill(prompt_text)

# Selección de parámetros (Modo DJ, Loop, Duración 30s/60s/120s)
# Si existen chips de estilo o sliders de afinación, se configuran programáticamente
```

### 4. Trigger de Generación y Detección de Estado
```python
# Clic en el botón generar
gen_button = page.locator('button:has-text("Generate"), button:has-text("Crear"), button:has-text("Generar")').first
await gen_button.click()

# Esperar a que el spinner desaparezca y el reproductor de audio / botón de descarga esté activo
await page.wait_for_selector('audio, button[aria-label*="Download"], button:has-text("Descargar")', timeout=90000)
```

### 5. Extracción Limpia del Archivo de Audio (Estrategia Dual)
1. **Vía Evento de Descarga de Playwright**:
   ```python
   async with page.expect_download(timeout=15000) as download_info:
       download_btn = page.locator('button[aria-label*="Download"], button:has-text("Descargar")').first
       await download_btn.click()
   download = await download_info.value
   await download.save_as(target_raw_audio_path)
   ```
2. **Vía Extracción Directa de Memoria (Blob / Buffer JS)** si no hay botón visible:
   ```javascript
   // Inyección JS para extraer el buffer de audio activo
   async () => {
       const audioEl = document.querySelector('audio');
       if (!audioEl || !audioEl.src) return null;
       const response = await fetch(audioEl.src);
       const blob = await response.blob();
       return new Promise((resolve) => {
           const reader = new FileReader();
           reader.onloadend = () => resolve(reader.result);
           reader.readAsDataURL(blob);
       });
   }
   ```

---

## 5. Post-Procesamiento Inmediato: De Raw IA a Master Audiófilo

Una vez descargado el audio crudo (`.wav` o `.mp3`), el runner **no entrega un archivo sin tratar**. Automáticamente lo procesa con la cadena DSP de 8 etapas:
1. **Afinación Pitagórica 432Hz / 528Hz**: Reajuste de frecuencia fundamental mediante `rubberband` / phase-vocoder.
2. **Mono Sub-Bass (<80Hz)**: Colapso de bajas frecuencias para estabilidad en auriculares planares y conos de graves.
3. **Crossfeed Meier Binaural**: Algoritmo BS2B para eliminar la fatiga auditiva de la escucha en cascos.
4. **Mastering LUFS**: Normalización exacta a **-14.0 LUFS** (YouTube/Redes) o **-16.0 LUFS** (Modo Lujo Audiófilo).

---

## 6. Pipeline de Quema Masiva de Créditos (Batch Audio Factory)

Para aprovechar al máximo los créditos acumulados en Flow Music:
- **Generación en Lote Nocturna**: Se define un archivo JSON con 20–100 prompts clasificados por temas (Walking Tours, Documentales Espaciales, Cyberpunk, Meditación).
- **Cola Asíncrona con Rate-Limiting Suave**: El runner ejecuta una pista cada ~45 segundos, permitiendo enfriamiento de sesión y evitando throttling de Google Labs.
- **Auto-Catalogación**: Cada pista se etiqueta con BPM, tonalidad, metadata JSON y se registra en `VideoStorageManager` bajo `storage/music/flowmusic/`.
