#!/usr/bin/env node
// Genera la miniatura (1280x720) de un episodio:  node miniatura.js <config.json> <salida.png> [variante]
// Con varias propuestas en config.thumbs, [variante] elige cuál (0, 1, 2…).
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const [configPath, outPath, variant] = process.argv.slice(2);
if (!configPath || !outPath) { console.error("Uso: node miniatura.js <config.json> <salida.png>"); process.exit(2); }
(async () => {
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  if (config.thumbs) config.thumb = config.thumbs[Number(variant || 0)];
  if (!config.thumb) { console.error("El archivo no tiene el bloque 'thumb'"); process.exit(1); }
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.goto("file://" + path.join(__dirname, "miniatura.html"));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate((c) => window.initThumb(c), config);
  await page.evaluate(() => document.querySelector("#img").decode());
  const problems = await page.evaluate(() => window.thumbProblems);
  if (problems.length) { console.error(problems.join("\n")); await browser.close(); process.exit(1); }
  await page.screenshot({ path: outPath });
  await browser.close();
})();
