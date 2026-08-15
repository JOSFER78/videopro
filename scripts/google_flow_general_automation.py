#!/usr/bin/env python3
"""
google_flow_general_automation.py — Automatización de Google Flow con Gemini Omni Flash y VideoStorageManager.

Interactúa con la interfaz de Google Flow vía Chrome DevTools Protocol (CDP) usando Playwright.
Almacena todos los vídeos generados, clips y capturas dentro de la jerarquía canónica
del proyecto usando VideoStorageManager.
"""

import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

try:
    from video_storage_manager import VideoStorageManager
except ImportError:
    from scripts.video_storage_manager import VideoStorageManager

# ------------------------- Configuración -------------------------
GENERATION_PROMPT = os.getenv(
    "GENERATION_PROMPT",
    "Un video de un coche deportivo conduciendo por una carretera de montaña "
    "al atardecer, estilo cinematográfico, alta calidad"
)

# Tiempo máximo de espera para completar la generación (segundos)
MAX_WAIT_TIME = int(os.getenv("MAX_WAIT_TIME", "120"))


async def select_gemini_omni_flash(page):
    """Selecciona el modelo Gemini Omni Flash en Google Flow."""
    ultra_btn = page.get_by_text('ULTRA', exact=False)
    try:
        await ultra_btn.wait_for(state='visible', timeout=15000)
    except Exception as e:
        print(f"[ERROR] Botón ULTRA no encontrado: {e}")
        body_text = await page.inner_text('body')
        if 'ULTRA' in body_text:
            print("[WARN] Texto ULTRA encontrado en body pero no interactivo")
            print(f"Snippet: {body_text[:200]}...")
        raise RuntimeError("No se pudo localizar el botón de selección de modelo ULTRA") from e
    
    await ultra_btn.wait_for(state='attached', timeout=5000)
    
    box = await ultra_btn.bounding_box()
    if not box:
        print("[WARN] No se obtuvo bounding box para ULTRA, usando estimación")
        viewport = page.viewport_size
        if viewport:
            x = viewport['width'] // 2
            y = viewport['height'] // 3
            await page.mouse.click(x, y)
            print(f"[Stepping] Clic en ULTRA en coordenadas estimadas ({x}, {y})")
        else:
            raise RuntimeError("No se pudo obtener bounding box ni viewport size")
    else:
        x = box['x'] + box['width'] // 2
        y = box['y'] + box['height'] // 2
        await page.mouse.click(x, y)
        print(f"[Stepping] Clic en botón ULTRA en ({x}, {y})")
    
    await page.wait_for_timeout(2000)


async def pick_gemini_omni_flash_option(page):
    """Elige la opción Gemini Omni Flash del menú desplegable."""
    click_script = """
    () => {
        const options = Array.from(document.querySelectorAll('[role="option"], [role="menuitem"]'));
        for (const opt of options) {
            if (opt.innerText.trim() === 'Gemini Omni Flash') {
                opt.click();
                return true;
            }
        }
        for (const opt of options) {
            if (opt.innerText.trim().toLowerCase() === 'gemini omni flash') {
                opt.click();
                return true;
            }
        }
        console.warn('Opción Gemini Omni Flash no encontrada');
        return false;
    }
    """
    result = await page.evaluate(click_script)
    if not result:
        print("[WARN] No se pudo hacer clic en Gemini Omni Flash vía evaluate")
    else:
        print("[Stepping] Gemini Omni Flash seleccionado vía direct evaluation")
    
    await page.keyboard.press("Escape")
    await page.wait_for_timeout(1000)


async def input_generation_prompt(page, prompt: str):
    """Introduce el prompt de generación en el campo de texto."""
    await page.wait_for_timeout(2000)
    
    # Estrategia 1: Textarea visible que no sea reCAPTCHA
    textareas = page.locator('textarea')
    textarea_count = await textareas.count()
    print(f"[Stepping] Encontrados {textarea_count} elementos textarea")
    
    for i in range(textarea_count):
        ta = textareas.nth(i)
        is_visible = await ta.is_visible()
        if not is_visible:
            continue
        
        id_attr = await ta.get_attribute('id') or ''
        class_attr = await ta.get_attribute('class') or ''
        if 'g-recaptcha-response' in id_attr or 'g-recaptcha-response' in class_attr:
            continue
        
        print(f"[Stepping] Usando textarea [{i}] para prompt")
        await ta.wait_for(state='visible')
        await ta.fill(prompt)
        print("[Stepping] Prompt introducido en textarea")
        return
    
    # Estrategia 2: Input o textarea con 'texto' o 'prompt'
    inputs = page.locator('input, textarea')
    input_count = await inputs.count()
    for i in range(min(input_count, 10)):
        try:
            el = inputs.nth(i)
            placeholder = await el.get_attribute('placeholder') or ''
            aria_label = await el.get_attribute('aria-label') or ''
            if not await el.is_visible():
                continue
            
            if any(k in placeholder.lower() or k in aria_label.lower() for k in ['texto', 'prompt', 'describe', 'story']):
                print(f"[Stepping] Usando input [{i}] para prompt")
                await el.wait_for(state='visible')
                await el.fill(prompt)
                return
        except Exception:
            continue
    
    # Estrategia 3: Contenteditable
    content_editables = page.locator('[contenteditable="true"]')
    editable_count = await content_editables.count()
    for i in range(min(editable_count, 5)):
        try:
            el = content_editables.nth(i)
            if await el.is_visible():
                await el.click()
                await el.fill(prompt)
                return
        except Exception:
            continue
            
    raise RuntimeError("No se encontró el campo para ingresar el prompt")


async def click_generate_button(page):
    """Hace clic en el botón de generación."""
    await page.wait_for_timeout(2000)
    button_selectors = [
        'button:has-text("add_2Crear")',
        'button:has-text("Crear")',
        'button:has-text("Generar")',
        'button:has-text("Create")',
        'button:has-text("Generate")',
        'button[aria-label*="Crear"]',
        'button[aria-label*="Generar"]',
        'button[aria-label*="Create"]',
        'button[aria-label*="Generate"]',
    ]
    for selector in button_selectors:
        try:
            btn = page.locator(selector).first
            if await btn.count() > 0:
                await btn.wait_for(state='visible', timeout=5000)
                await btn.click()
                print(f"[Stepping] Clic en botón de generación: {selector}")
                return
        except Exception:
            continue
    raise RuntimeError("No se encontró el botón de generar/crear")


async def wait_for_generation_completion(page):
    """Espera a que finalice la generación en la UI."""
    print(f"[Stepping] Esperando que se complete la generación (hasta {MAX_WAIT_TIME}s)")
    poll_interval = 3
    elapsed = 0
    while elapsed < MAX_WAIT_TIME:
        download_btn = page.locator('button:has-text("Descargar"), button:has-text("Download")')
        if await download_btn.count() > 0:
            print("[Stepping] Botón de descarga detectado")
            return True

        video_elements = page.locator('video')
        if await video_elements.count() > 0:
            print("[Stepping] Elemento video detectado")
            return True

        page_text = await page.inner_text("body")
        if any(keyword in page_text.lower() for keyword in ["generado", "completado", "listo", "download", "descarg"]):
            print("[Stepping] Mensaje de finalización detectado en página")
            return True

        await page.wait_for_timeout(poll_interval * 1000)
        elapsed += poll_interval

    print("[WARN] Indicador de finalización no detectado dentro del timeout")
    return False


async def click_download_button(page):
    """Hace clic en el botón de descarga."""
    download_btn = page.locator('button:has-text("Descargar"), button:has-text("Download")')
    if await download_btn.count() == 0:
        download_btn = page.locator('button[aria-label*="Download"], button[aria-label*="Descargar"]')
        if await download_btn.count() == 0:
            print("[ERROR] No se encontró botón de descarga")
            return False

    print("[Stepping] Haciendo clic en descargar")
    try:
        await download_btn.wait_for(state="visible")
        await download_btn.click()
        print("[Stepping] Clic de descarga completado")
        return True
    except Exception as e:
        print(f"[ERROR] Falló el clic de descarga: {e}")
        return False


async def main(project_ref: str = None, prompt: str = None, output_filename: str = "google_flow_clip.mp4"):
    """Flujo de automatización unificado con VideoStorageManager."""
    storage = VideoStorageManager(project_ref=project_ref, title="Google Flow Video Generation")
    output_video_path = storage.get_asset_path("flow_videos", output_filename)
    prompt_to_use = prompt or GENERATION_PROMPT

    print("[INIT] Inicializando automatización Google Flow con VideoStorageManager")
    print(f"Proyecto Canónico: {storage.project_dir}")
    print(f"Ruta Canónica Destino: {output_video_path}")
    print(f"Ruta Screenshots: {storage.screenshots_dir}")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp('http://localhost:9222')
            context = browser.contexts[0]
        except Exception as e:
            print(f"[ERROR] No se pudo conectar a Chrome por CDP (puerto 9222): {e}")
            return

        page = None
        for pg in context.pages:
            if 'labs.google/fx' in pg.url and 'flow' in pg.url:
                page = pg
                break
        if not page:
            page = context.pages[0] if context.pages else await context.new_page()

        print(f"[INIT] Usando página: {page.url}")

        # Guardar captura inicial en screenshots_dir
        init_screenshot = storage.get_screenshot_path("flow_initial_state.png")
        await page.screenshot(path=str(init_screenshot))

        # Paso 1: Seleccionar Gemini Omni Flash
        try:
            await select_gemini_omni_flash(page)
            await pick_gemini_omni_flash_option(page)
        except Exception as e:
            print(f"[WARN] Error seleccionando modelo: {e}")

        # Paso 2: Introducir prompt
        await input_generation_prompt(page, prompt_to_use)

        # Paso 3: Generar
        await click_generate_button(page)

        # Paso 4: Esperar finalización
        completed = await wait_for_generation_completion(page)
        if not completed:
            print("[INFO] Esperando tiempo fijo adicional...")
            await page.wait_for_timeout(MAX_WAIT_TIME * 1000)

        # Captura post-generación
        done_screenshot = storage.get_screenshot_path("flow_after_generation.png")
        await page.screenshot(path=str(done_screenshot))

        # Paso 5: Descarga
        success = await click_download_button(page)
        if success:
            await page.wait_for_timeout(5000)
            if output_video_path.exists() and output_video_path.stat().st_size >= 5000:
                storage.register_asset(
                    name=output_filename,
                    asset_type="flow_videos",
                    source_path=output_video_path,
                    source_engine="google_flow_omni",
                    metadata={"prompt": prompt_to_use}
                )
                print(f"[SUCCESS] Vídeo validado y registrado en: {output_video_path}")
            else:
                print(f"[INFO] Descarga iniciada. Guardar clip en: {output_video_path}")

        await browser.close()
        print("[DONE] Automatización de Google Flow finalizada.")


if __name__ == "__main__":
    proj_arg = sys.argv[1] if len(sys.argv) > 1 else None
    prompt_arg = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        asyncio.run(main(proj_arg, prompt_arg))
    except Exception as exc:
        print(f"[FATAL ERROR] {exc}")
        sys.exit(1)
