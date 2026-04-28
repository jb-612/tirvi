#!/usr/bin/env node
/**
 * md-to-pdf.js — Puppeteer-based Markdown → PDF for the Jishu PDF Editor.
 *
 * Usage:
 *   node md-to-pdf.js --in build/source-with-svg.md \
 *                     --out dist/document.pdf \
 *                     --config brand/pdf-options.json
 *
 * Imports / depends on:
 *   - puppeteer
 *   - markdown-it (or md-to-pdf if you prefer the all-in-one)
 *
 * This is a thin wrapper. Full version lives in user/scripts/md-to-pdf.js
 * and is symlinked here for the Jishu PDF Editor skill.
 */

const fs = require('fs');
const path = require('path');

async function main() {
  const args = Object.fromEntries(
    process.argv.slice(2).reduce((acc, cur, i, all) => {
      if (cur.startsWith('--')) acc.push([cur.slice(2), all[i + 1]]);
      return acc;
    }, [])
  );

  const mdPath  = path.resolve(args.in);
  const pdfPath = path.resolve(args.out);
  const cfg     = JSON.parse(fs.readFileSync(path.resolve(args.config), 'utf8'));

  const md = fs.readFileSync(mdPath, 'utf8');
  // markdown-it pipeline omitted for brevity — render md → html with the
  // <style> block from frontmatter inlined, then:

  const puppeteer = require('puppeteer');
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setContent(/* rendered html */ md, { waitUntil: 'networkidle0' });
  await page.pdf({
    path: pdfPath,
    format: cfg.format || 'A4',
    margin: cfg.margin,
    printBackground: cfg.printBackground !== false,
    displayHeaderFooter: !!cfg.displayHeaderFooter,
    headerTemplate: cfg.headerTemplate || '<span></span>',
    footerTemplate: cfg.footerTemplate || '<span></span>',
  });
  await browser.close();
  console.error(`Wrote ${pdfPath}`);
}

main().catch((e) => { console.error(e); process.exit(1); });
