#!/usr/bin/env node
/**
 * build.js — Convert source-with-svg.md → standalone HTML for Chrome --print-to-pdf
 *
 * Usage:
 *   cd docs/articles/agentic-layering
 *   npm install --no-save markdown-it markdown-it-footnote markdown-it-attrs gray-matter
 *   node build.js
 */
const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');
const MarkdownIt = require('markdown-it');
const footnote = require('markdown-it-footnote');
const attrs = require('markdown-it-attrs');

const SRC = path.resolve(__dirname, 'build/source-with-svg.md');
const HTML_OUT = path.resolve(__dirname, 'build/agentic-layering.html');
const BRAND_CSS = fs.readFileSync(
  path.resolve(__dirname, 'brand/colors_and_type.css'),
  'utf8'
);

const raw = fs.readFileSync(SRC, 'utf8');
const { content, data: fm } = matter(raw);

const md = new MarkdownIt({ html: true, linkify: true, typographer: true })
  .use(footnote)
  .use(attrs);

let body = md.render(content);

// Resolve diagram <img> src to absolute paths so file:// loads them
body = body.replace(/src="build\/diagrams\//g, 'src="diagrams/');

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${fm.title || 'Document'}</title>
<style>
${BRAND_CSS}

@page { size: A4; margin: 22mm 18mm 22mm 18mm; }

* { box-sizing: border-box; }
html, body {
  background: var(--paper);
  color: var(--ink);
  font-family: var(--font-body);
  font-size: 10.5pt;
  line-height: 1.5;
  margin: 0;
  padding: 0;
}
.container { max-width: 174mm; margin: 0 auto; padding: 0 0 30mm 0; }
h1, h2, h3, h4 { font-family: var(--font-display); color: var(--clay); page-break-after: avoid; }
h1 { font-size: 28pt; line-height: 1.1; margin: 0 0 .3em 0; letter-spacing: -0.5px; }
h2 { font-size: 17pt; line-height: 1.2; margin: 1.5em 0 .4em; border-top: 2px solid var(--clay); padding-top: .6em; color: var(--clay); }
h3 { font-size: 12pt; font-family: var(--font-display); color: var(--ink); margin: 1.1em 0 .3em; font-style: italic; font-weight: 500; }
h4 { font-size: 10.5pt; font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.08em; color: var(--ink-60); margin: .9em 0 .2em; }
p { margin: .5em 0 .8em; orphans: 3; widows: 3; }
.lede { font-family: var(--font-display); font-style: italic; font-size: 13pt; color: var(--ink-90); max-width: 60ch; margin: .5em 0 1em; line-height: 1.4; }
.eyebrow { font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.16em; font-size: 8.5pt; color: var(--clay); display: block; margin-bottom: 1em; }
hr { border: 0; border-top: 1px solid var(--ink-12); margin: 1.5em 0; }
strong { color: var(--ink); font-weight: 600; }
em { font-style: italic; }
blockquote { border-left: 2px solid var(--clay); padding: .3em 0 .3em 1em; font-style: italic; font-family: var(--font-display); margin: 1em 0; color: var(--ink-90); }
code { font-family: var(--font-mono); font-size: 9.5pt; color: var(--clay-deep); background: var(--paper-ink); padding: 1px 5px; border-radius: 2px; }
pre { background: var(--ink); color: var(--paper); padding: 12px 14px; border-radius: 4px; overflow-x: auto; font-size: 9pt; line-height: 1.4; page-break-inside: avoid; }
pre code { background: transparent; color: inherit; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 1em 0 1.4em; font-size: 9.5pt; page-break-inside: avoid; }
table th { background: var(--paper-deep); font-family: var(--font-mono); text-transform: uppercase; font-size: 8.5pt; letter-spacing: 0.04em; padding: 8px 10px; text-align: left; border-bottom: 2px solid var(--ink); color: var(--ink); }
table td { padding: 6px 10px; vertical-align: top; border-bottom: 1px solid var(--ink-12); }
table tr:nth-child(even) td { background: rgba(43,33,26,0.02); }
img.diagram { display: block; margin: 1.5em auto; max-width: 100%; max-height: 100mm; page-break-inside: avoid; }
ul, ol { margin: .4em 0 1em; padding-left: 1.4em; }
li { margin: .25em 0; }
.footnotes { margin-top: 2em; padding-top: 1em; border-top: 1px solid var(--ink-12); font-size: 9pt; }
.footnotes ol { padding-left: 2em; }
.footnotes li { margin: .35em 0; }
.footnotes p { display: inline; margin: 0; }
.footnote-ref a { color: var(--clay); text-decoration: none; font-family: var(--font-mono); font-size: .8em; vertical-align: super; }
.footnote-backref { color: var(--ink-40); text-decoration: none; font-size: .8em; }
a { color: var(--clay-deep); }
sup { font-size: .75em; }

/* Cover */
.cover {
  height: 254mm;
  display: flex; flex-direction: column; justify-content: space-between;
  page-break-after: always;
  background: linear-gradient(180deg, var(--paper-deep) 0%, var(--paper) 60%);
  padding: 16mm 16mm 12mm;
  margin: -8mm -8mm 8mm; /* nudge to bleed */
}
.cover h1 { font-size: 40pt; line-height: 1.05; margin: 0; color: var(--ink); font-style: italic; max-width: 16ch; }
.cover h1 .accent { color: var(--clay); font-style: italic; }
.cover .subtitle { font-family: var(--font-display); font-style: italic; font-size: 14pt; color: var(--ink-60); margin: 1em 0 0; max-width: 56ch; line-height: 1.4; }
.cover .meta { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10mm; font-size: 9pt; }
.cover .meta dt { font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.12em; color: var(--ink-60); margin: 0 0 4px; font-size: 8pt; }
.cover .meta dd { font-family: var(--font-body); margin: 0; color: var(--ink); font-weight: 500; }
.cover .rule { width: 80mm; height: 4px; background: var(--clay); margin: 1.4em 0; }
.brand-mark { display: flex; align-items: center; gap: 8px; font-family: var(--font-display); font-style: italic; font-size: 16pt; color: var(--ink); }
.brand-mark .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--clay); }
</style>
</head>
<body>
<div class="container">
<section class="cover">
  <div>
    <div class="brand-mark">Jishu<span class="dot"></span></div>
  </div>
  <div>
    <h1>How You Could <span class="accent">Do Better</span></h1>
    <p class="subtitle">${fm.subtitle || ''}</p>
    <div class="rule"></div>
    <dl class="meta">
      <div><dt>Author</dt><dd>${fm.author || ''}</dd></div>
      <div><dt>Published</dt><dd>${fm.date || ''}</dd></div>
      <div><dt>Status</dt><dd>${fm.status || ''}</dd></div>
    </dl>
  </div>
</section>
${body}
</div>
</body>
</html>
`;

fs.writeFileSync(HTML_OUT, html, 'utf8');
console.error(`Wrote ${HTML_OUT} (${html.length} chars)`);
