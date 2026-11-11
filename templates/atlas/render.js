#!/usr/bin/env node
/*
 * Renderiza la plantilla "Atlas" a vídeo.
 *
 *   node render.js <config.json> <salida.mp4> [--audio voz.wav] [--fps 25] [--still seg]
 *
 * config.visuals admite fotos y vídeos (p. ej. clips de Flow), con rutas relativas a la plantilla. Las fotos se
 * animan en la propia página; los vídeos se colocan en el escenario con FFmpeg, debajo de los rótulos. Antes de renderizar
 * comprueba en todo el vídeo que ningún texto se sale de su caja; si algo falla, no genera nada.
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

(async () => {
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  const missing = config.visuals.filter((v) => !fs.existsSync(path.join(__dirname, v.src)));
  if (missing.length) { console.error("Faltan imágenes: " + missing.map((v) => v.src).join(", ")); process.exit(1); }

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto("file://" + path.join(__dirname, "atlas.html"));
  await page.evaluate((c) => window.initHud(c), config);
  await page.evaluate(() => document.fonts.ready);
  const draw = async (t) => {
    await page.evaluate((x) => window.renderHud(x), t);
    // cada imagen debe estar decodificada antes de capturar
    await page.evaluate(() => Promise.all([...document.images].filter((i) => i.src).map((i) => i.decode().catch(() => {}))));
  };

  const problems = new Set();
  for (let t = 0; t <= config.duration; t += 0.25) {
    await draw(t);
    for (const p of await page.evaluate(() => window.checkLayout())) problems.add(`${t.toFixed(1)}s  ${p}`);
  }
  if (problems.size) {
    console.error("Maquetación incorrecta:\n  " + [...problems].slice(0, 20).join("\n  "));
    await browser.close(); process.exit(1);
  }
  console.log("maquetación comprobada: ningún texto se sale ni se pisa");

  const stage = await page.evaluate(() => window.STAGE);
  const flags = await page.evaluate((list) => list.map((src) => window.isVideoSrc(src)), config.visuals.map((v) => v.src));
  const videos = config.visuals.map((v, i) => ({ ...v, end: config.visuals[i + 1]?.at ?? config.duration })).filter((_, i) => flags[i]);

  if (still !== null) {
    await draw(Number(still));
    await page.screenshot({ path: outPath, omitBackground: true });
    await browser.close();
    if (videos.length) console.log("nota: con --still los tramos de vídeo salen con el escenario transparente");
    return;
  }

  const work = fs.mkdtempSync(path.join(os.tmpdir(), "atlas-"));
  const total = Math.round(config.duration * fps);
  for (let f = 0; f < total; f++) {
    await draw(f / fps);
    if (videos.length) await page.screenshot({ path: path.join(work, `f${String(f).padStart(5, "0")}.png`), omitBackground: true });
    else await page.screenshot({ path: path.join(work, `f${String(f).padStart(5, "0")}.jpg`), type: "jpeg", quality: 95 });
    if (f % 150 === 0) console.log(`fotograma ${f}/${total}`);
  }
  await browser.close();
  let ff;
  if (!videos.length) {
    ff = ["-y", "-v", "error", "-framerate", String(fps), "-i", path.join(work, "f%05d.jpg")];
    if (audio) ff.push("-i", audio, "-c:a", "aac", "-b:a", "192k");
  } else {
    // fondo → cada vídeo en el hueco del escenario durante su tramo → rótulos con transparencia
    ff = ["-y", "-v", "error"];
    videos.forEach((v) => ff.push("-ss", String(v.start || 0), "-t", String(v.end - v.at + 1), "-i", path.join(__dirname, v.src)));
    ff.push("-framerate", String(fps), "-i", path.join(work, "f%05d.png"));
    if (audio) ff.push("-i", audio);
    const n = videos.length;
    let graph = `color=c=0x0c0d0f:s=1920x1080:r=${fps}[b0];`, last = "b0";
    videos.forEach((v, i) => {
      graph += `[${i}:v]scale=${stage.w}:${stage.h}:force_original_aspect_ratio=increase,crop=${stage.w}:${stage.h},fps=${fps},setsar=1,setpts=PTS-STARTPTS+${v.at}/TB[v${i}];` +
               `[${last}][v${i}]overlay=${stage.x}:${stage.y}:eof_action=pass:enable='between(t,${v.at},${v.end + 1})'[b${i + 1}];`;
      last = `b${i + 1}`;
    });
    graph += `[${last}][${n}:v]overlay=0:0[out]`;
    ff.push("-filter_complex", graph, "-map", "[out]");
    if (audio) ff.push("-map", `${n + 1}:a`, "-c:a", "aac", "-b:a", "192k");
  }
  ff.push("-t", String(config.duration), "-r", String(fps), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", outPath);
  const res = spawnSync("ffmpeg", ff, { stdio: "inherit" });
  fs.rmSync(work, { recursive: true, force: true });
  process.exit(res.status ?? 1);
})();
