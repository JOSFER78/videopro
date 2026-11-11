#!/usr/bin/env node
/*
 * Renderiza la plantilla "Cuaderno".
 *
 *   node render.js <config.json> <salida.mp4> [--audio voz.wav] [--fps 25] [--still seg]
 *
 * El vídeo o la imagen de cada tramo se indica en config.footage ([{at, file, start}]) y se coloca
 * DENTRO del marco dibujado (nunca a pantalla completa), con un tono de papel para que no desentone.
 * Capas: papel → metraje en el hueco → rótulos dibujados. Con --still guarda un PNG de ese segundo.
 */
const { chromium } = require("playwright");
const { spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const args = process.argv.slice(2);
const flag = (name) => { const i = args.indexOf(`--${name}`); return i === -1 ? null : args.splice(i, 2)[1]; };
const audio = flag("audio"), still = flag("still");
const fps = Number(flag("fps") || 25);
const [configPath, outPath] = args;
if (!configPath || !outPath) {
  console.error("Uso: node render.js <config.json> <salida.mp4|png> [--audio a.wav] [--fps 25] [--still seg]");
  process.exit(2);
}
// Tono de papel para el metraje: menos saturación y negros levantados
const GRADE = "eq=saturation=0.62:contrast=0.94,curves=all='0/0.08 1/0.94'";

(async () => {
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  const base = path.dirname(path.resolve(configPath));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto("file://" + path.join(__dirname, "cuaderno.html"));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => document.body.classList.add("hud-only"));   // el papel de fondo lo pone FFmpeg
  await page.evaluate((c) => window.initHud(c), config);
  const stage = await page.evaluate(() => window.STAGE);

  // Antes de renderizar: en todo el vídeo, nada se pisa ni se sale de su caja
  const problems = new Set();
  for (let t = 0; t <= config.duration; t += 0.25) {
    await page.evaluate((x) => window.renderHud(x), t);
    for (const p of await page.evaluate(() => window.checkLayout())) problems.add(`${t.toFixed(1)}s  ${p}`);
  }
  if (problems.size) {
    console.error("Maquetación incorrecta:\n  " + [...problems].slice(0, 20).join("\n  "));
    await browser.close(); process.exit(1);
  }
  console.log("maquetación comprobada: nada se pisa ni se sale");

  const work = fs.mkdtempSync(path.join(os.tmpdir(), "cuaderno-"));
  const shot = async (file, t) => {
    await page.evaluate((x) => window.renderHud(x), t);
    await page.screenshot({ path: file, omitBackground: true });
  };

  // Lista de tramos de metraje → un clip continuo del tamaño del hueco
  const missing = (config.footage || []).filter((f) => !fs.existsSync(path.resolve(base, f.file)));
  if (missing.length) console.warn("AVISO: falta metraje, el escenario quedará en blanco en esos tramos: " + missing.map((f) => f.file).join(", "));
  const footage = (config.footage || []).filter((f) => !missing.includes(f)).map((f, i, all) => ({
    ...f, file: path.resolve(base, f.file), dur: (all[i + 1] ? all[i + 1].at : config.duration) - f.at }));
  const stageClip = (t0, dur, out) => {
    const inputs = [], parts = [];
    footage.forEach((f, i) => {
      inputs.push("-ss", String(f.start || 0), "-t", String(f.dur), "-i", f.file);
      parts.push(`[${i}:v]scale=${stage.w}:${stage.h}:force_original_aspect_ratio=increase,crop=${stage.w}:${stage.h},fps=${fps},setsar=1,${GRADE}[s${i}]`);
    });
    const lead = footage.length ? footage[0].at : config.duration;
    const chain = [`color=c=0xe9e6dc:s=${stage.w}x${stage.h}:r=${fps}:d=${Math.max(lead, 0.04)}[lead]`, ...parts,
      `[lead]${footage.map((_, i) => `[s${i}]`).join("")}concat=n=${footage.length + 1}:v=1:a=0[st]`];
    return { inputs, chain };
  };

  if (still !== null) {
    const hud = path.join(work, "hud.png");
    await shot(hud, Number(still));
    await browser.close();
    const { inputs, chain } = stageClip();
    const n = footage.length;
    const ff = ["-y", "-v", "error", ...inputs, "-i", hud, "-filter_complex",
      `${chain.join(";")};color=c=0xe9e6dc:s=1920x1080:r=${fps}[bg];[st]trim=start=${still},setpts=PTS-STARTPTS[st1];[bg][st1]overlay=${stage.x}:${stage.y}:shortest=1[b];[b][${n}:v]overlay[v]`,
      "-map", "[v]", "-frames:v", "1", outPath];
    const r = spawnSync("ffmpeg", ff, { stdio: "inherit" });
    fs.rmSync(work, { recursive: true, force: true });
    process.exit(r.status ?? 1);
  }

  const total = Math.round(config.duration * fps);
  for (let f = 0; f < total; f++) {
    await shot(path.join(work, `f${String(f).padStart(5, "0")}.png`), f / fps);
    if (f % 150 === 0) console.log(`fotograma ${f}/${total}`);
  }
  await browser.close();

  const { inputs, chain } = stageClip();
  const n = footage.length;
  const ff = ["-y", "-v", "error", ...inputs, "-framerate", String(fps), "-i", path.join(work, "f%05d.png")];
  if (audio) ff.push("-i", audio);
  ff.push("-filter_complex",
    `${chain.join(";")};color=c=0xe9e6dc:s=1920x1080:r=${fps}[bg];[bg][st]overlay=${stage.x}:${stage.y}:eof_action=pass[b];[b][${n}:v]overlay[v]`,
    "-map", "[v]");
  if (audio) ff.push("-map", `${n + 1}:a`, "-c:a", "aac", "-b:a", "192k");
  ff.push("-t", String(config.duration), "-r", String(fps), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", outPath);
  const res = spawnSync("ffmpeg", ff, { stdio: "inherit" });
  fs.rmSync(work, { recursive: true, force: true });
  process.exit(res.status ?? 1);
})();
