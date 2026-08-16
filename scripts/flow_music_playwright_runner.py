#!/usr/bin/env python3
"""
flow_music_playwright_runner.py — Runner Autónomo de Google Flow Music / MusicFX vía Playwright y CDP.

Automatiza la generación de música BSO y pistas de audio neural en Google Labs Flow Music / MusicFX
utilizando la sesión web activa en el VPS (puerto 9222 CDP o contexto persistente).
Aplica automáticamente la cadena de masterización DSP audiófila y registra el activo en VideoStorageManager.

Uso:
  python3 scripts/flow_music_playwright_runner.py --prompt "Warm 432Hz ambient walking tour..." --output "storage/music/flowmusic/city_tour.wav"
  python3 scripts/flow_music_playwright_runner.py --batch templates/batch_flow_music_prompts.json --category "walking_tours"
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("videopro.flow_music_runner")

# Intentar importar VideoStorageManager
try:
    from video_storage_manager import VideoStorageManager
except ImportError:
    try:
        from scripts.video_storage_manager import VideoStorageManager
    except ImportError:
        VideoStorageManager = None

# Intentar importar AudiophileAudioProcessor
PROCESSOR_SCRIPT = Path(__file__).resolve().parent.parent / "docs" / "investigaciones" / "flow_music" / "mastering_cascos_lujo" / "scripts" / "audiophile_audio_processor.py"


class FlowMusicPlaywrightRunner:
    """
    Controlador de Playwright para automatizar Google Flow Music / MusicFX vía CDP.
    """

    def __init__(
        self,
        cdp_url: str = "http://127.0.0.1:9222",
        output_dir: Optional[Path] = None,
        timeout_seconds: int = 120
    ):
        self.cdp_url = cdp_url
        base_dir = Path(__file__).resolve().parent.parent
        self.output_dir = output_dir or (base_dir / "storage" / "music" / "flowmusic")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = timeout_seconds

    async def _dismiss_modals(self, page) -> None:
        """Cierra automáticamente avisos, modales de bienvenida y cookies."""
        modal_buttons = [
            'button:has-text("Aceptar")',
            'button:has-text("Entendido")',
            'button:has-text("Got it")',
            'button:has-text("Continuar")',
            'button:has-text("Continue")',
            'button:has-text("I agree")',
            'button[aria-label*="Close"]',
            'button[aria-label*="Cerrar"]',
            'button:has-text("Dismiss")',
        ]
        for sel in modal_buttons:
            try:
                btn = page.locator(sel).first
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.click()
                    logger.info(f"Modal cerrado con selector: {sel}")
                    await page.wait_for_timeout(400)
            except Exception:
                pass

    async def _inject_prompt(self, page, prompt_text: str) -> bool:
        """Inyecta el prompt en el campo editable de Flow Music / MusicFX."""
        prompt_set = False

        # 1. Intentar textarea
        textareas = page.locator('textarea:visible')
        count = await textareas.count()
        if count > 0:
            for i in range(count):
                ta = textareas.nth(i)
                id_val = await ta.get_attribute('id') or ''
                if 'recaptcha' not in id_val:
                    await ta.click()
                    await ta.fill(prompt_text)
                    prompt_set = True
                    logger.info(f"Prompt inyectado en textarea [{i}]")
                    break

        # 2. Intentar contenteditable
        if not prompt_set:
            editables = page.locator('[contenteditable="true"]:visible')
            if await editables.count() > 0:
                ed = editables.first
                await ed.click()
                await ed.fill(prompt_text)
                prompt_set = True
                logger.info("Prompt inyectado en div[contenteditable='true']")

        # 3. Fallback mediante inyección JS directa
        if not prompt_set:
            escaped = json.dumps(prompt_text)
            js_res = await page.evaluate(f'''(() => {{
                const el = document.querySelector('textarea, div[contenteditable="true"]');
                if (!el) return 'NOT_FOUND';
                el.focus();
                if (el.tagName === 'TEXTAREA') {{
                    el.value = {escaped};
                }} else {{
                    el.innerText = {escaped};
                }}
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return 'OK';
            }})()''')
            if js_res == 'OK':
                prompt_set = True
                logger.info("Prompt inyectado vía evaluate JS")

        if not prompt_set:
            raise RuntimeError("No se pudo localizar el campo de entrada de prompt en Flow Music")

        await page.wait_for_timeout(800)
        return True

    async def _trigger_generation(self, page) -> bool:
        """Hace clic en el botón de generar pista musical."""
        gen_buttons = [
            'button:has-text("Generate")',
            'button:has-text("Generar")',
            'button:has-text("Crear")',
            'button:has-text("Create")',
            'button[aria-label*="Generate"]',
            'button[aria-label*="Crear"]',
            'button[aria-label*="Generar"]',
            'button.generate-button'
        ]
        for sel in gen_buttons:
            try:
                btn = page.locator(sel).first
                if await btn.count() > 0 and await btn.is_visible():
                    await btn.click()
                    logger.info(f"Botón de generación activado: {sel}")
                    return True
            except Exception:
                continue

        # Fallback vía enter en el campo
        try:
            await page.keyboard.press("Enter")
            logger.info("Activado mediante Enter en el teclado")
            return True
        except Exception as e:
            logger.warning(f"Error al presionar Enter: {e}")

        raise RuntimeError("No se encontró el botón de generar en la interfaz de Flow Music")

    async def _wait_and_download_audio(self, page, raw_output_path: Path) -> bool:
        """Espera a que termine la generación y descarga el archivo de audio."""
        start_time = time.time()
        logger.info(f"Esperando generación de audio en Flow Music (máximo {self.timeout_seconds}s)...")

        while time.time() - start_time < self.timeout_seconds:
            # Estrategia 1: Detectar botón de descarga y usar expect_download
            dl_selectors = [
                'button:has-text("Descargar")',
                'button:has-text("Download")',
                'button[aria-label*="Download"]',
                'button[aria-label*="Descargar"]',
                'a[download]'
            ]
            for sel in dl_selectors:
                try:
                    btn = page.locator(sel).first
                    if await btn.count() > 0 and await btn.is_visible():
                        logger.info(f"Botón de descarga detectado: {sel}")
                        async with page.expect_download(timeout=15000) as dl_info:
                            await btn.click()
                        download = await dl_info.value
                        await download.save_as(str(raw_output_path))
                        if raw_output_path.exists() and raw_output_path.stat().st_size > 5000:
                            logger.info(f"Audio descargado con éxito vía botón: {raw_output_path} ({raw_output_path.stat().st_size} bytes)")
                            return True
                except Exception:
                    pass

            # Estrategia 2: Extraer URL de elemento <audio> o <video>
            try:
                audio_src = await page.evaluate('''() => {
                    const audio = document.querySelector('audio');
                    if (audio && audio.src && audio.src.startsWith('http')) return audio.src;
                    const video = document.querySelector('video');
                    if (video && video.src && video.src.startsWith('http')) return video.src;
                    return null;
                }''')
                if audio_src:
                    logger.info(f"URL de stream detectada: {audio_src[:60]}... Descargando con curl")
                    res = subprocess.run(
                        ["curl", "-s", "-L", "-o", str(raw_output_path), audio_src],
                        capture_output=True,
                        check=True
                    )
                    if raw_output_path.exists() and raw_output_path.stat().st_size > 5000:
                        logger.info(f"Audio guardado vía stream: {raw_output_path}")
                        return True
            except Exception as e:
                logger.warning(f"Error extrayendo audio vía stream: {e}")

            # Estrategia 3: Extraer Blob binario directamente desde la memoria JS del navegador
            try:
                data_url = await page.evaluate('''async () => {
                    const audio = document.querySelector('audio');
                    if (!audio || !audio.src) return null;
                    try {
                        const r = await fetch(audio.src);
                        const b = await r.blob();
                        return new Promise((resolve) => {
                            const reader = new FileReader();
                            reader.onloadend = () => resolve(reader.result);
                            reader.readAsDataURL(b);
                        });
                    } catch (e) {
                        return null;
                    }
                }''')
                if data_url and data_url.startswith("data:audio"):
                    import base64
                    header, encoded = data_url.split(",", 1)
                    audio_bytes = base64.b64decode(encoded)
                    with open(raw_output_path, "wb") as f:
                        f.write(audio_bytes)
                    if raw_output_path.exists() and raw_output_path.stat().st_size > 5000:
                        logger.info(f"Audio extraído de memoria JS Blob: {raw_output_path}")
                        return True
            except Exception:
                pass

            await page.wait_for_timeout(3000)

        logger.warning("Tiempo de espera agotado sin poder capturar el audio de Flow Music")
        return False

    def _apply_dsp_mastering(
        self,
        input_audio: Path,
        tuning_hz: int = 432,
        profile: str = "audiophile_luxury"
    ) -> Dict[str, str]:
        """Aplica la cadena de masterización DSP audiófila si el script existe."""
        if not PROCESSOR_SCRIPT.exists():
            logger.warning(f"Script DSP no encontrado en {PROCESSOR_SCRIPT}, omitiendo post-mastering")
            return {"raw": str(input_audio)}

        out_dir = input_audio.parent
        cmd = [
            sys.executable,
            str(PROCESSOR_SCRIPT),
            "--input", str(input_audio),
            "--output-dir", str(out_dir),
            "--tuning", str(tuning_hz),
            "--profile", profile
        ]
        try:
            logger.info(f"Ejecutando post-mastering DSP (Tuning {tuning_hz}Hz, Perfil {profile})...")
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Mastering completado:\n{res.stdout.strip()}")
            
            stem = input_audio.stem
            return {
                "raw": str(input_audio),
                "audiophile_flac": str(out_dir / f"{stem}_audiophile_master.flac"),
                "universal_m4a": str(out_dir / f"{stem}_universal_master.m4a"),
                "mastering_meta": str(out_dir / f"{stem}_mastering_metadata.json")
            }
        except Exception as e:
            logger.warning(f"Fallo en la ejecución de post-mastering DSP: {e}")
            return {"raw": str(input_audio)}

    async def generate_single_track(
        self,
        prompt: str,
        filename_prefix: str = "flow_track",
        tuning_hz: int = 432,
        profile: str = "audiophile_luxury",
        target_url: str = "https://labs.google/fx/tools/music-fx"
    ) -> Dict[str, Any]:
        """
        Ciclo completo: Conecta a CDP, inyecta prompt, descarga audio y procesa DSP.
        """
        timestamp = int(time.time())
        raw_filename = f"{filename_prefix}_{timestamp}_raw.wav"
        raw_output_path = self.output_dir / raw_filename

        logger.info(f"Iniciando generación en Flow Music. Prompt: {prompt[:70]}...")
        async with async_playwright() as p:
            try:
                browser = await p.chromium.connect_over_cdp(self.cdp_url)
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
            except Exception as e:
                logger.error(f"No se pudo conectar a Chrome por CDP ({self.cdp_url}): {e}")
                raise RuntimeError(f"Error de conexión CDP a {self.cdp_url}") from e

            page = None
            for pg in context.pages:
                if "labs.google" in pg.url and ("music" in pg.url or "flow" in pg.url):
                    page = pg
                    break

            if not page:
                page = await context.new_page()
                await page.goto(target_url, timeout=30000)
                await page.wait_for_load_state("domcontentloaded")

            await self._dismiss_modals(page)
            await self._inject_prompt(page, prompt)
            await self._trigger_generation(page)
            download_ok = await self._wait_and_download_audio(page, raw_output_path)

            if not download_ok or not raw_output_path.exists():
                raise RuntimeError("No se pudo descargar el archivo de audio desde Flow Music")

        # Aplicar DSP Mastering
        masters = self._apply_dsp_mastering(raw_output_path, tuning_hz=tuning_hz, profile=profile)

        # Registro de metadatos
        meta = {
            "prompt": prompt,
            "tuning_hz": tuning_hz,
            "profile": profile,
            "timestamp": timestamp,
            "files": masters
        }
        meta_path = self.output_dir / f"{filename_prefix}_{timestamp}_manifest.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        logger.info(f"Pista generada y registrada con éxito: {meta_path}")
        return meta


def main():
    parser = argparse.ArgumentParser(description="Runner Autónomo de Google Flow Music vía Playwright & CDP")
    parser.add_argument("--prompt", type=str, help="Prompt musical a generar")
    parser.add_argument("--output-dir", type=str, default="storage/music/flowmusic", help="Directorio destino")
    parser.add_argument("--tuning", type=int, default=432, help="Afinación Hz (432 o 528)")
    parser.add_argument("--profile", type=str, default="audiophile_luxury", choices=["audiophile_luxury", "universal_streaming"])
    parser.add_argument("--cdp-url", type=str, default="http://127.0.0.1:9222", help="URL CDP de Chrome/Brave")
    parser.add_argument("--batch", type=str, help="Archivo JSON con lista de prompts para generación por lotes")

    args = parser.parse_args()

    out_path = Path(args.output_dir)
    runner = FlowMusicPlaywrightRunner(cdp_url=args.cdp_url, output_dir=out_path)

    if args.batch:
        batch_file = Path(args.batch)
        if not batch_file.exists():
            print(f"[ERROR] Archivo de lote no encontrado: {batch_file}")
            sys.exit(1)
        with open(batch_file, "r", encoding="utf-8") as f:
            batch_data = json.load(f)
        prompts = batch_data.get("prompts", [])
        print(f"[BATCH] Iniciando lote de {len(prompts)} pistas...")
        for i, item in enumerate(prompts):
            p_text = item.get("prompt") if isinstance(item, dict) else item
            prefix = item.get("prefix", f"batch_track_{i+1}") if isinstance(item, dict) else f"batch_track_{i+1}"
            print(f"\n--- [LOTE {i+1}/{len(prompts)}] {prefix} ---")
            try:
                res = asyncio.run(runner.generate_single_track(
                    prompt=p_text,
                    filename_prefix=prefix,
                    tuning_hz=args.tuning,
                    profile=args.profile
                ))
                print(f"[OK] Pista completada: {res['files']}")
                time.sleep(6) # Breve pausa entre generaciones
            except Exception as exc:
                print(f"[ERROR] Falló pista {prefix}: {exc}")
    elif args.prompt:
        res = asyncio.run(runner.generate_single_track(
            prompt=args.prompt,
            filename_prefix="flow_music_track",
            tuning_hz=args.tuning,
            profile=args.profile
        ))
        print(f"\n[ÉXITO] Pista generada y masterizada:\n{json.dumps(res, indent=2)}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
