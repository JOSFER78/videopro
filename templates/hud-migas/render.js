#!/usr/bin/env node
/*
 * Renderiza la plantilla HUD "Migas" sobre un vídeo.
 *
 *   node render.js <config.json> <salida.mp4> [--video fondo.mp4] [--audio voz.mp3] [--fps 25] [--still 12.5]
 *
 * Captura el HUD con fondo transparente fotograma a fotograma y lo compone con FFmpeg.
 * Sin --video usa un fondo neutro de prueba. Con --still guarda un PNG de ese segundo y termina.
 */
const { chromium } = require("playwright");
const { spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const args = process.argv.slice(2);
const flag = (name) => { const i = args.indexOf(`--${name}`); return i === -1 ? null : args.splice(i, 2)[1]; };
const video = flag("video"), audio = flag("audio"), still = flag("still");
const fps = Number(flag("fps") || 25);
const [configPath, outPath] = args;
if (!configPath || !outPath) {
  console.error("Uso: node render.js <config.json> <salida.mp4|png> [--video f.mp4] [--audio a.mp3] [--fps 25] [--still seg]");
  process.exit(2);
}

(async () => {
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto("file://" + path.join(__dirname, "hud.html"));
  await page.evaluate((c) => window.initHud(c), config);
  await page.evaluate(() => document.fonts.ready);

  // Antes de renderizar: comprobar en todo el vídeo que nada se pisa ni se sale de pantalla
  const problems = new Set();
  for (let t = 0; t <= config.duration; t += 0.2) {
    await page.evaluate((x) => window.renderHud(x), t);
    for (const p of await page.evaluate(() => window.checkLayout())) problems.add(`${t.toFixed(1)}s  ${p}`);
  }
  if (problems.size) {
    console.error("Maquetación incorrecta:\n  " + [...problems].slice(0, 20).join("\n  "));
    await browser.close();
    process.exit(1);
  }
  console.log("maquetación comprobada: nada se pisa ni se sale");

  if (still !== null) {
    await page.evaluate((t) => window.renderHud(t), Number(still));
    await page.screenshot({ path: outPath, omitBackground: !video });
    await browser.close();
    return;
  }

  const frames = fs.mkdtempSync(path.join(os.tmpdir(), "hud-"));
  const total = Math.round(config.duration * fps);
  for (let f = 0; f < total; f++) {
    await page.evaluate((t) => window.renderHud(t), f / fps);
    await page.screenshot({ path: path.join(frames, `f${String(f).padStart(5, "0")}.png`), omitBackground: true });
    if (f % 100 === 0) console.log(`fotograma ${f}/${total}`);
  }
  await browser.close();

  const bg = video
    ? ["-stream_loop", "-1", "-i", video]
    : ["-f", "lavfi", "-i", `color=c=0x1d1d1f:s=1920x1080:r=${fps},noise=alls=7:allf=t`];
  const ff = ["-y", "-v", "error", ...bg, "-framerate", String(fps), "-i", path.join(frames, "f%05d.png")];
  if (audio) ff.push("-i", audio);
  ff.push("-filter_complex", "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080[bg];[bg][1:v]overlay=format=auto[v]",
          "-map", "[v]");
  if (audio) ff.push("-map", "2:a", "-c:a", "aac", "-b:a", "192k");
  ff.push("-t", String(config.duration), "-r", String(fps), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", outPath);
  const res = spawnSync("ffmpeg", ff, { stdio: "inherit" });
  fs.rmSync(frames, { recursive: true, force: true });
  process.exit(res.status ?? 1);
})();
