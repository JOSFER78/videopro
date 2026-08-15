"""
google_flow_runner.py — Runner desatendido de Google Flow vía Playwright / CDP (Modo 3).

Automatiza la generación de clips en Google Flow usando Gemini Omni Flash en Display :99 / CDP 9222.
Inyecta la foto de referencia (Keyframe 0) en el slot de ingredientes, envía el prompt cinematográfico 7D
y descarga el archivo MP4 generado.
"""

import asyncio
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

from loguru import logger


async def _dismiss_modals(page):
    """Cierra popups, modales de bienvenida o advertencias en Google Flow."""
    modal_buttons = [
        'button:has-text("Aceptar")',
        'button:has-text("Entendido")',
        'button:has-text("Got it")',
        'button:has-text("Continuar")',
        'button:has-text("Continue")',
        'button[aria-label*="Close"]',
        'button[aria-label*="Cerrar"]',
    ]
    for sel in modal_buttons:
        try:
            btn = page.locator(sel).first
            if await btn.count() > 0 and await btn.is_visible():
                await btn.click()
                await page.wait_for_timeout(500)
        except Exception:
            pass


async def _select_gemini_omni_flash(page):
    """Selecciona el modelo Gemini Omni Flash."""
    try:
        # Buscar botón selector de modelo
        model_btn = page.locator('button:has-text("ULTRA"), button:has-text("Ultra"), button:has-text("Model")').first
        if await model_btn.count() > 0 and await model_btn.is_visible():
            await model_btn.click()
            await page.wait_for_timeout(1000)
            
            # Buscar opción Gemini Omni Flash
            omni_opt = page.locator('[role="option"]:has-text("Gemini Omni Flash"), [role="menuitem"]:has-text("Gemini Omni Flash")').first
            if await omni_opt.count() > 0 and await omni_opt.is_visible():
                await omni_opt.click()
                logger.info("Selected Gemini Omni Flash model")
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)
    except Exception as e:
        logger.warning(f"Could not switch model explicitly (using default): {e}")


async def _inject_ingredient_image(page, image_path: str):
    """Sube la imagen maestra al slot de ingredientes de Google Flow."""
    img_file = Path(image_path)
    if not img_file.exists():
        logger.warning(f"Ingredient image not found: {image_path}")
        return False

    try:
        file_inputs = page.locator('input[type="file"]')
        count = await file_inputs.count()
        if count > 0:
            for i in range(count):
                inp = file_inputs.nth(i)
                try:
                    await inp.set_input_files(str(img_file.resolve()))
                    logger.success(f"Ingredient image injected to file input [{i}]: {img_file.name}")
                    await page.wait_for_timeout(1500)
                    return True
                except Exception:
                    continue
        logger.warning("No suitable file input found for ingredient upload")
        return False
    except Exception as e:
        logger.warning(f"Failed to inject ingredient image: {e}")
        return False


async def _input_prompt_and_generate(page, prompt: str):
    """Introduce el prompt y hace clic en el botón de generar."""
    # Textarea o contenteditable
    prompt_set = False
    textareas = page.locator('textarea:visible')
    if await textareas.count() > 0:
        for i in range(await textareas.count()):
            ta = textareas.nth(i)
            id_val = await ta.get_attribute('id') or ''
            if 'recaptcha' not in id_val:
                await ta.fill(prompt)
                prompt_set = True
                break

    if not prompt_set:
        editables = page.locator('[contenteditable="true"]:visible')
        if await editables.count() > 0:
            ed = editables.first
            await ed.click()
            await ed.fill(prompt)
            prompt_set = True

    if not prompt_set:
        raise RuntimeError("No input field found for Google Flow prompt")

    await page.wait_for_timeout(1000)

    # Clic en botón Generar / Crear
    button_selectors = [
        'button:has-text("add_2Crear")',
        'button:has-text("Crear")',
        'button:has-text("Generar")',
        'button:has-text("Create")',
        'button:has-text("Generate")',
        'button[aria-label*="Crear"]',
        'button[aria-label*="Generar"]',
    ]
    for sel in button_selectors:
        try:
            btn = page.locator(sel).first
            if await btn.count() > 0 and await btn.is_visible():
                await btn.click()
                logger.info(f"Clicked generate button: {sel}")
                return True
        except Exception:
            continue

    raise RuntimeError("No generation button found in Google Flow UI")


async def _wait_and_download_clip(page, output_mp4_path: str, timeout_seconds: int = 180) -> bool:
    """Espera la finalización del render y descarga el archivo MP4."""
    out_file = Path(output_mp4_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    start_time = time.time()

    logger.info(f"Waiting for Google Flow generation (max {timeout_seconds}s)...")
    while time.time() - start_time < timeout_seconds:
        # 1. Comprobar si hay botón de descarga disponible
        dl_btn = page.locator('button:has-text("Descargar"), button:has-text("Download"), button[aria-label*="Download"]').first
        if await dl_btn.count() > 0 and await dl_btn.is_visible():
            logger.info("Download button detected, initiating download")
            try:
                async with page.expect_download(timeout=15000) as download_info:
                    await dl_btn.click()
                download = await download_info.value
                await download.save_as(str(out_file))
                if out_file.exists() and out_file.stat().st_size > 10000:
                    logger.success(f"Downloaded Google Flow video: {out_file} ({out_file.stat().st_size} bytes)")
                    return True
            except Exception as e:
                logger.warning(f"Standard download trigger failed: {e}, checking video element src")

        # 2. Comprobar si hay elemento video con src cargado
        video_el = page.locator('video').first
        if await video_el.count() > 0:
            src = await video_el.get_attribute('src')
            if src and src.startswith("http"):
                logger.info(f"Video element src detected: {src[:60]}... Fetching directly")
                try:
                    res = subprocess.run(
                        ["curl", "-s", "-L", "-o", str(out_file), src],
                        capture_output=True,
                        check=True
                    )
                    if out_file.exists() and out_file.stat().st_size > 10000:
                        logger.success(f"Captured video via stream URL: {out_file}")
                        return True
                except Exception as e:
                    logger.warning(f"Curl download of video src failed: {e}")

        await page.wait_for_timeout(3000)

    logger.warning("Google Flow generation wait timed out")
    return False


async def run_google_flow_job(
    prompt: str,
    output_mp4_path: str,
    image_reference: Optional[str] = None,
    timeout_seconds: int = 180,
) -> dict:
    """
    Ejecuta el ciclo completo de Google Flow conectándose a CDP localhost:9222.
    Si la sesión web requiere reautenticación o no está disponible, realiza un fallback
    de síntesis visual con motion 2.5D para no interrumpir el montaje del vídeo.
    """
    from playwright.async_api import async_playwright

    logger.info(f"Initiating Google Flow job for scene. Target: {output_mp4_path}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0] if browser.contexts else await browser.new_context()

            flow_page = None
            for pg in context.pages:
                if "labs.google" in pg.url or "flow" in pg.url:
                    flow_page = pg
                    break

            if not flow_page:
                flow_page = await context.new_page()
                await flow_page.goto("https://labs.google/fx/tools/flow", timeout=30000)
                await flow_page.wait_for_load_state("domcontentloaded")

            await _dismiss_modals(flow_page)
            await _select_gemini_omni_flash(flow_page)

            if image_reference and os.path.exists(image_reference):
                await _inject_ingredient_image(flow_page, image_reference)

            await _input_prompt_and_generate(flow_page, prompt)
            success = await _wait_and_download_clip(flow_page, output_mp4_path, timeout_seconds=timeout_seconds)

            if success and os.path.exists(output_mp4_path):
                return {
                    "success": True,
                    "clip_path": output_mp4_path,
                    "engine": "google_flow_omni",
                }
    except Exception as exc:
        logger.warning(f"Google Flow CDP automation encountered an issue: {exc}")

    # Fallback elegante: si CDP o Flow no pudieron descargar el clip, sintetizar escena con FLUX 2.5D
    logger.info("Generating cinematic clip fallback via FLUX 2.5D engine...")
    from app.services.flux_keyframe import generate_flux_keyframe, synthesize_flux_clip

    temp_img = output_mp4_path.replace(".mp4", "_keyframe.png")
    generate_flux_keyframe(prompt, temp_img, reference_image=image_reference)
    synthesize_flux_clip(temp_img, output_mp4_path, duration=5.0)
    return {
        "success": True,
        "clip_path": output_mp4_path,
        "engine": "flux_fallback",
        "notice": "Rendered via FLUX 2.5D cinematic fallback",
    }


def generate_google_flow_clip_sync(
    prompt: str,
    output_mp4_path: str,
    image_reference: Optional[str] = None,
    timeout_seconds: int = 180,
) -> dict:
    """Wrapper sincrónico para ser invocado desde los workers de task.py."""
    return asyncio.run(
        run_google_flow_job(
            prompt=prompt,
            output_mp4_path=output_mp4_path,
            image_reference=image_reference,
            timeout_seconds=timeout_seconds,
        )
    )
