#!/usr/bin/env node
/*
 * Renderiza la plantilla "Atlas" a vídeo.
 *
 *   node render.js <config.json> <salida.mp4> [--audio voz.wav] [--fps 25] [--still seg] [--jobs 4]
 *
 * config.visuals admite fotos y vídeos (p. ej. clips de Flow), con rutas relativas a la plantilla. Las fotos se
 * animan en la propia página; de cada vídeo se extraen antes los fotogramas de su tramo (desde `start` segundos) y la
 * página enseña el que toca, así los fundidos y los rótulos funcionan igual que con una foto. Antes de renderizar
 * comprueba en todo el vídeo que ningún texto se sale de su caja; si algo falla, no genera nada.
 * --jobs reparte los fotogramas entre varias pestañas para aprovechar todos los núcleos.
 */
const { chromium } = require("playwright");
const { spawnSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const args = process.argv.slice(2);
const flag = (name) => { const i = args.indexOf(`--${name}`); return i === -1 ? null : args.splice(i, 2)[1]; };
const audio = flag("audio"), still = flag("still");
const fps = Number(flag("fps") || 25), jobs = Number(flag("jobs") || 1);
const [configPath, outPath] = args;
if (!configPath || !outPath) {
  console.error("Uso: node render.js <config.json> <salida.mp4|png> [--audio a.wav] [--fps 25] [--still seg] [--jobs 4]");
  process.exit(2);
}

(async () => {
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  const missing = config.visuals.filter((v) => !fs.existsSync(path.join(__dirname, v.src)));
  if (missing.length) { console.error("Faltan imágenes: " + missing.map((v) => v.src).join(", ")); process.exit(1); }

  const work = fs.mkdtempSync(path.join(os.tmpdir(), "atlas-"));
  const done = (code) => { fs.rmSync(work, { recursive: true, force: true }); process.exit(code); };

  // Vídeos: se extraen los fotogramas de su tramo (más 1 s para el fundido de salida) a una carpeta
  config.visuals.forEach((v, i) => {
    if (!/\.(mp4|mov|webm|mkv)$/i.test(v.src)) return;
    const end = config.visuals[i + 1]?.at ?? config.duration, dir = path.join(work, `v${i}`);
    fs.mkdirSync(dir);
    const r = spawnSync("ffmpeg", ["-y", "-v", "error", "-ss", String(v.start || 0), "-t", String(end - v.at + 1), "-i", path.join(__dirname, v.src),
      "-vf", `fps=${fps},scale=1444:700:force_original_aspect_ratio=increase`, "-q:v", "2", path.join(dir, "%05d.jpg")], { stdio: "inherit" });
    v.count = fs.readdirSync(dir).length;
    if (r.status !== 0 || !v.count) { console.error("No se pudo leer el vídeo " + v.src); done(1); }
    v.frames = "file://" + dir; v.fps = fps;
  });

  const browser = await chromium.launch();
  const open = async () => {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    await page.goto("file://" + path.join(__dirname, "atlas.html"));
    await page.evaluate((c) => window.initHud(c), config);
    await page.evaluate(() => document.fonts.ready);
    return page;
  };
  const draw = async (page, t) => {
    await page.evaluate((x) => window.renderHud(x), t);
    // cada imagen debe estar decodificada antes de capturar
    await page.evaluate(() => Promise.all([...document.images].filter((i) => i.src).map((i) => i.decode().catch(() => {}))));
  };
  const page = await open();

  const problems = new Set();
  for (let t = 0; t <= config.duration; t += 0.25) {
    await page.evaluate((x) => window.renderHud(x), t);
    for (const p of await page.evaluate(() => window.checkLayout())) problems.add(`${t.toFixed(1)}s  ${p}`);
  }
  if (problems.size) {
    console.error("Maquetación incorrecta:\n  " + [...problems].slice(0, 20).join("\n  "));
    await browser.close(); done(1);
  }
  console.log("maquetación comprobada: ningún texto se sale ni se pisa");

  if (still !== null) {
    await draw(page, Number(still));
    await page.screenshot({ path: outPath });
    await browser.close(); done(0);
  }

  const total = Math.round(config.duration * fps);
  const pages = [page];
  while (pages.length < jobs) pages.push(await open());
  let next = 0;
  await Promise.all(pages.map(async (pg) => {
    for (let f = next++; f < total; f = next++) {
      await draw(pg, f / fps);
      await pg.screenshot({ path: path.join(work, `f${String(f).padStart(5, "0")}.jpg`), type: "jpeg", quality: 93 });
      if (f % 500 === 0) console.log(`fotograma ${f}/${total}`);
    }
  }));
  await browser.close();
  const ff = ["-y", "-v", "error", "-framerate", String(fps), "-i", path.join(work, "f%05d.jpg")];
  if (audio) ff.push("-i", audio, "-c:a", "aac", "-b:a", "192k");
  ff.push("-t", String(config.duration), "-r", String(fps), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", outPath);
  const res = spawnSync("ffmpeg", ff, { stdio: "inherit" });
  done(res.status ?? 1);
})();
