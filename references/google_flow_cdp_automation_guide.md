# Guía Técnica: Automatización Autónoma de Google Flow vía CDP & Websockets

Esta guía documenta el estándar de interacción programática con **Google Flow** (`labs.google/fx/tools/flow`) utilizando el protocolo Chrome DevTools (CDP) sobre sesiones activas en Chromium/Brave.

---

## 1. Arquitectura de Conexión

```
┌─────────────────┐       HTTP JSON       ┌──────────────────────┐
│  Hermes Agent   │ ───────────────────►  │  Chromium CDP :9223  │
│  (Python CDP)   │ ◄───────────────────  │  (labs.google/flow)  │
└─────────────────┘      Websockets       └──────────────────────┘
```

1. **Descubrimiento de Pestaña**:
   - `GET http://127.0.0.1:9223/json`
   - Filtrar la pestaña donde `url` contiene `labs.google/fx/tools/flow/project/`
   - Obtener `webSocketDebuggerUrl` (`ws://127.0.0.1:9223/devtools/page/<ID>`)

2. **Conexión Websocket con Buffer Ampliado**:
   - Para transferencias de imágenes 4K y metraje de video, abrir conexión con `max_size=50*1024*1024` (50MB).

---

## 2. Inyección de Prompts y Control del Prompt Drawer

En Google Flow, el área de texto principal es un `div[contenteditable="true"]`:

```python
escaped_prompt = json.dumps(prompt_text)
set_expr = f'''(() => {{
    const div = document.querySelector('div[contenteditable="true"]');
    if (!div) return 'NO_DIV';
    div.focus();
    div.innerText = {escaped_prompt};
    div.dispatchEvent(new Event('input', {{ bubbles: true }}));
    div.dispatchEvent(new Event('change', {{ bubbles: true }}));
    return 'OK';
}})()'''
```

### Envío de la Petición
```python
click_expr = '''(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const sendBtn = btns.find(b => b.innerText.includes('arrow_forward') || b.innerText.includes('Crear'));
    if (sendBtn) {
        sendBtn.click();
        return 'CLICKED';
    }
    return 'NO_BTN';
})()'''
```

---

## 3. Configuración de Parámetros del Agente (Settings Panel)

Para evitar bloqueos de confirmación manual:
1. Abrir el panel de ajustes (`button` con texto `Ajustes` o icono `tune`).
2. Seleccionar la opción **"Nunca"** en *Confirmar antes de generar*.
3. Definir relación de aspecto (**16:9**) y modelo predeterminado (**Omni Flash** para video, **Nano Banana 2 / Pro** para imágenes).
4. Pulsar **"Guardar"**.

---

## 4. Extracción y Descarga Directa de Medios Generados

Las imágenes y clips generados se sirven a través del endpoint firmado de Google Labs:
`https://labs.google/fx/api/trpc/media.getMediaUrlRedirect?name=...`

Para descargarlos preservando las cookies de sesión activa sin provocar errores CORS o de autenticación:

```javascript
(async () => {
    const imgs = Array.from(document.querySelectorAll('img')).filter(i => i.src && i.src.includes('media.getMediaUrlRedirect'));
    if (imgs.length === 0) return null;
    const latest = imgs[imgs.length - 1];
    const res = await fetch(latest.src);
    const blob = await res.blob();
    const reader = new FileReader();
    return new Promise((resolve) => {
        reader.onloadend = () => resolve(reader.result);
        reader.readAsDataURL(blob);
    });
})()
```

El resultado en formato `data:image/png;base64,...` se decodifica en Python y se guarda directamente en el directorio local del proyecto.
