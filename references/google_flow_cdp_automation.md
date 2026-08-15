# Guía Definitiva de Automatización de Google Flow vía Chromium CDP

## 1. Lanzamiento del Navegador y Persistencia de Sesión
Para interactuar con Google Flow sin tropezar con la detección de bots de OAuth ("This browser or app may not be secure"), se debe reutilizar la instancia nativa del perfil Chromium en el servidor VPS:

```bash
# Eliminar posibles bloqueos obsoletos de Singleton
rm -f /home/ubuntu/.config/chromium/Singleton*

# Iniciar Chromium nativo de Snap en la pantalla Xvfb :99 con depuración remota en puerto 9223
DISPLAY=:99 snap run chromium --remote-debugging-port=9223 --no-sandbox &
```

**Ventajas:**
- Mantiene las cookies activas de la cuenta Google Ultra (`josferestudio@gmail.com`).
- Evita el bloqueo OAuth de bots en headless Playwright genérico.

---

## 2. Conexión CDP con Playwright (Python)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9223")
    context = browser.contexts[0]
    page = context.pages[0]
```

---

## 3. Manejo Autónomo de Modales y Banners

1. **Banner de Cookies:**
   - Debe descartarse antes de interactuar con botones de acción para evitar la interceptación de eventos de puntero (`glue-cookie-notification-bar`):
   ```python
   cookie_btn = page.query_selector('button:has-text("OK, got it")')
   if cookie_btn:
       cookie_btn.click()
   ```

2. **Selección de Cuenta Google:**
   - Si la sesión requiere re-autenticación visual:
   ```python
   acc = page.query_selector('text=josferestudio@gmail.com')
   if acc:
       acc.click()
   ```

3. **Navegación al Proyecto:**
   - En Storyboard Studio (`https://labs.google/fx/es/tools/flow/shared/tool/79c9d2e6-4ad6-4636-ad05-22022f8a5a74`), seleccionar un proyecto de la lista y presionar `button:has-text("Abrir")`.

---

## 4. Inserción de Prompts y Generación (Slate.js Editor)

Caja de prompt en Slate.js:
- Selector CSS: `div[role="textbox"][contenteditable="true"]`

```python
tb = page.query_selector('div[role="textbox"][contenteditable="true"]')
tb.click()
page.keyboard.press("Control+A")
page.keyboard.press("Backspace")
page.keyboard.type(prompt_text)

# Enviar a renderizado
create_btn = page.query_selector('button:has-text("Crear")')
if create_btn:
    create_btn.click()
```

---

## 5. Descarga de Activos y Verificación
- Las imágenes generadas se renderizan en el canvas en elementos `<img>` con URLs `https://lh3.googleusercontent.com/...` o blobs.
- Captura de pantalla o descarga HTTP directa -> guardar en `assets/images/` y validar tamaño > 5 KB con Pillow.
