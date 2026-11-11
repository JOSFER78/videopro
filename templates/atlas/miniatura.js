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
  let variantes = config.thumbs || (config.thumb ? [config.thumb] : []);
  if (variant !== undefined) variantes = variantes.slice(Number(variant), Number(variant) + 1);   // solo esa variante
  if (!variantes.length) { console.error("El archivo no tiene miniaturas ('thumbs' o 'thumb')"); process.exit(1); }
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  for (let i = 0; i < variantes.length; i++) {
    await page.goto("file://" + path.join(__dirname, "miniatura.html"));
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate((c) => window.initThumb(c), { ...config, thumb: variantes[i] });
    await page.evaluate(() => document.querySelector("#img").decode());
    const problems = await page.evaluate(() => window.thumbProblems);
    if (problems.length) { console.error(problems.join("\n")); await browser.close(); process.exit(1); }
    // con varias variantes: salida_1.png, salida_2.png…
    const destino = variantes.length > 1 ? outPath.replace(/(\.\w+)$/, `_${i + 1}$1`) : outPath;
    await page.screenshot({ path: destino });
    console.log(destino);
  }
  await browser.close();
})();
