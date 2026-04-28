---
pdf_options:
  format: A4
  margin: 0
  printBackground: true
  displayHeaderFooter: false
  preferCSSPageSize: false
body_class: jishu-brief
css: |
  body { margin: 0; padding: 0; }
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500;1,6..72,600&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --paper: #F4ECE0;
  --paper-deep: #EAE0D0;
  --paper-soft: #FAF4EB;
  --paper-ink: #E0D4C0;
  --ink: #2B211A;
  --ink-90: rgba(43,33,26,0.90);
  --ink-60: rgba(43,33,26,0.60);
  --ink-40: rgba(43,33,26,0.40);
  --ink-24: rgba(43,33,26,0.24);
  --ink-12: rgba(43,33,26,0.12);
  --ink-06: rgba(43,33,26,0.06);
  --clay: #C35A3A;
  --clay-deep: #A64828;
  --clay-soft: #E8A88F;
  --clay-wash: #F6E0D4;
  --ochre: #C98B3A;
  --ochre-deep: #A06E22;
  --ochre-wash: #F4E6CC;
  --sage: #7B8A6F;
  --sage-wash: #DDE3D4;
  --olive-deep: #4F5A3E;
  --success: #5C7C4F;
  --warning: #A06E22;
  --danger: #B53D28;
  --info: #4E6B78;
  --font-display: 'Newsreader', 'Iowan Old Style', Cambria, Georgia, serif;
  --font-body: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
}

@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--paper); color: var(--ink); font-family: var(--font-body); -webkit-print-color-adjust: exact; print-color-adjust: exact; }

.sheet {
  position: relative;
  width: 210mm;
  height: 297mm;
  max-height: 297mm;
  overflow: hidden;
  page-break-after: always;
  background: var(--paper);
  padding: 22mm 18mm 24mm 18mm;
  font-size: 10.5pt;
  line-height: 1.5;
}
.sheet:last-child { page-break-after: auto; }

.bar-top, .bar-bot {
  position: absolute; left: 18mm; right: 18mm;
  font-family: var(--font-mono); font-size: 7.5pt;
  letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--ink-60);
  display: flex; justify-content: space-between; align-items: center;
}
.bar-top { top: 10mm; }
.bar-bot { bottom: 10mm; }
.bar-top .brand, .bar-bot .brand {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--font-display); font-style: italic; font-weight: 500;
  font-size: 11pt; letter-spacing: -0.5px; text-transform: none; color: var(--ink);
}
.bar-top .brand .dot {
  width: 5px; height: 5px; border-radius: 50%; background: var(--clay);
}
.bar-top .brand .meta {
  margin-left: 8px; padding-left: 8px;
  border-left: 1px solid var(--ink-12);
  color: var(--ink-60);
  font-family: var(--font-mono); font-size: 7.5pt;
  letter-spacing: 0.16em; text-transform: uppercase;
  font-style: normal; font-weight: 400;
}

h1, h2, h3, h4 { font-family: var(--font-display); color: var(--ink); margin: 0; font-weight: 500; page-break-after: avoid; }
h1 { font-size: 38pt; line-height: 1.05; letter-spacing: -1px; }
h2 { font-size: 24pt; line-height: 1.15; letter-spacing: -0.4px; margin: 0 0 4mm 0; }
h3 { font-size: 14pt; line-height: 1.2; margin: 0 0 2mm 0; }
.eyebrow {
  font-family: var(--font-mono); font-size: 8pt; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--clay); font-weight: 500;
  margin: 0 0 6mm 0;
}
.eyebrow.ink { color: var(--ink-60); }
.lede {
  font-family: var(--font-display); font-size: 14pt; line-height: 1.45;
  color: var(--ink-90); font-weight: 400; max-width: 130mm;
}
p { margin: 0 0 3mm 0; max-width: 165mm; }
.muted { color: var(--ink-60); }
.tiny { font-size: 8pt; }
.mono { font-family: var(--font-mono); }
.serif-ital { font-family: var(--font-display); font-style: italic; }
.clay { color: var(--clay); }
.ink { color: var(--ink); }
em.accent { color: var(--clay); font-style: italic; font-family: var(--font-display); }

/* COVER */
.cover {
  padding: 0;
  background: linear-gradient(160deg, var(--paper) 0%, var(--paper-deep) 100%);
}
.cover-inner {
  position: absolute; inset: 22mm 18mm 22mm 18mm;
  display: flex; flex-direction: column; justify-content: space-between;
}
.cover-eyebrow {
  font-family: var(--font-mono); font-size: 9pt; letter-spacing: 0.32em;
  text-transform: uppercase; color: var(--clay-deep); font-weight: 500;
}
.cover-mark {
  display: inline-flex; align-items: center; gap: 10px;
  font-family: var(--font-display); font-style: italic; font-weight: 500;
  font-size: 16pt; color: var(--ink);
}
.cover-mark .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--clay); }
.cover-title {
  font-family: var(--font-display); font-size: 76pt; font-weight: 500;
  line-height: 0.96; letter-spacing: -2.5px; color: var(--ink); margin: 0;
}
.cover-rule {
  width: 64mm; height: 2.4pt; background: var(--clay); margin: 6mm 0 8mm 0;
}
.cover-lede {
  font-family: var(--font-display); font-style: italic; font-size: 16pt;
  line-height: 1.45; color: var(--ink-90); max-width: 145mm; font-weight: 400;
}
.cover-meta {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 10mm;
  border-top: 1px solid var(--ink-12); padding-top: 6mm;
  font-family: var(--font-mono); font-size: 8pt; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--ink-60);
}
.cover-meta dt { font-size: 7.5pt; margin-bottom: 1mm; color: var(--ink-40); }
.cover-meta dd { font-size: 9pt; color: var(--ink); margin: 0; font-weight: 500; letter-spacing: 0.04em; }

/* TOC */
.toc-list { list-style: none; padding: 0; margin: 6mm 0 0 0; counter-reset: toc; }
.toc-list li {
  counter-increment: toc;
  display: grid; grid-template-columns: 12mm 1fr auto;
  align-items: end; padding: 4mm 0;
  border-bottom: 1px dotted var(--ink-24);
  font-size: 11.5pt;
}
.toc-list li::before {
  content: counter(toc, decimal-leading-zero);
  font-family: var(--font-mono); font-weight: 500; font-size: 10pt;
  letter-spacing: 0.1em; color: var(--clay);
}
.toc-list .title { font-family: var(--font-display); font-size: 13pt; color: var(--ink); }
.toc-list .sub { font-family: var(--font-body); font-size: 8.5pt; color: var(--ink-60); display: block; letter-spacing: 0.04em; }
.toc-list .pg { font-family: var(--font-mono); font-size: 9pt; letter-spacing: 0.1em; color: var(--ink-60); }

/* HERO STATS */
.hero-stat {
  display: flex; align-items: baseline; gap: 8mm;
  border-left: 3pt solid var(--clay); padding: 4mm 0 4mm 6mm; margin: 8mm 0;
}
.hero-stat .num {
  font-family: var(--font-display); font-size: 56pt; line-height: 0.95;
  font-weight: 500; letter-spacing: -2px; color: var(--ink);
}
.hero-stat .lbl {
  font-family: var(--font-body); font-size: 10pt; line-height: 1.45;
  color: var(--ink-90); max-width: 95mm;
}
.hero-stat .src { font-family: var(--font-mono); font-size: 7.5pt;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-60); display: block; margin-top: 1.5mm; }

.kpi-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 6mm; margin: 8mm 0 4mm 0;
}
.kpi {
  background: var(--paper-soft); border: 1px solid var(--ink-12);
  border-top: 3pt solid var(--clay); padding: 6mm 6mm 7mm 6mm;
}
.kpi .num {
  font-family: var(--font-display); font-size: 38pt; line-height: 1; font-weight: 500;
  color: var(--ink); letter-spacing: -1.4px; display: block;
}
.kpi .num small { font-size: 18pt; vertical-align: 0.2em; color: var(--clay); margin-left: 0.05em; font-weight: 500; }
.kpi .lbl { font-family: var(--font-body); font-size: 9pt; line-height: 1.4; color: var(--ink-90); margin-top: 2.5mm; display: block; }
.kpi .src { font-family: var(--font-mono); font-size: 6.5pt; letter-spacing: 0.18em; text-transform: uppercase; color: var(--ink-60); margin-top: 3mm; display: block; }
.kpi.ochre { border-top-color: var(--ochre); }
.kpi.sage { border-top-color: var(--sage); }
.kpi.ink-rule { border-top-color: var(--ink); }

/* PULL QUOTE */
.pull {
  font-family: var(--font-display); font-style: italic;
  font-size: 13pt; line-height: 1.5; color: var(--ink);
  border-left: 2pt solid var(--clay); padding: 0 0 0 5mm; max-width: 95mm;
}
.pull cite {
  display: block; margin-top: 3mm;
  font-family: var(--font-mono); font-style: normal; font-size: 7.5pt;
  letter-spacing: 0.16em; text-transform: uppercase; color: var(--ink-60);
}

/* GRID + CARDS */
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6mm; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8mm; }
.grid-2-asym { display: grid; grid-template-columns: 5fr 4fr; gap: 8mm; align-items: start; }
.card {
  background: var(--paper-soft); border: 1px solid var(--ink-12);
  padding: 5mm 5mm 5mm 5mm;
}
.card .num-mono {
  font-family: var(--font-mono); font-size: 8.5pt; font-weight: 500;
  letter-spacing: 0.2em; text-transform: uppercase; color: var(--clay);
  display: block; margin-bottom: 2mm;
}
.card h3 { font-family: var(--font-display); font-size: 13pt; margin: 0 0 2mm 0; }
.card p { font-size: 9.5pt; line-height: 1.5; color: var(--ink-90); margin: 0; }

/* TABLE */
table.cmp { width: 100%; border-collapse: collapse; font-size: 9pt; margin: 4mm 0; }
table.cmp th {
  font-family: var(--font-mono); font-size: 7.5pt; letter-spacing: 0.16em;
  text-transform: uppercase; font-weight: 500; color: var(--ink-90);
  background: var(--paper-deep); border-bottom: 2pt solid var(--ink); padding: 3mm 4mm;
  text-align: left;
}
table.cmp td {
  padding: 3mm 4mm; border-bottom: 1px solid var(--ink-12);
  vertical-align: middle; color: var(--ink-90);
}
table.cmp tr:nth-child(even) td { background: rgba(43,33,26,0.02); }
table.cmp tr.tirvi td { background: var(--clay-wash); color: var(--ink); font-weight: 500; }
table.cmp tr.tirvi td:first-child { color: var(--clay-deep); font-weight: 600; }
.dot-full, .dot-half, .dot-none {
  display: inline-block; width: 11px; height: 11px; border-radius: 50%;
  vertical-align: -1px;
}
.dot-full { background: var(--ink); }
.dot-half { background: linear-gradient(90deg, var(--ink) 0 50%, transparent 50% 100%); border: 1px solid var(--ink-40); }
.dot-none { background: transparent; border: 1px solid var(--ink-40); }
.legend { font-family: var(--font-mono); font-size: 7pt; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-60); margin-top: 3mm; }
.legend span { margin-right: 10mm; }

/* PIPELINE DIAGRAM */
.pipeline {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 0; align-items: stretch;
  margin: 8mm 0;
}
.pipeline .stage {
  position: relative; padding: 6mm 5mm 6mm 5mm; min-height: 36mm;
  background: var(--paper-soft); border: 1px solid var(--ink-12);
}
.pipeline .stage.moat {
  background: var(--clay-wash); border-color: var(--clay-soft); border-top: 3pt solid var(--clay);
}
.pipeline .stage .num-mono {
  font-family: var(--font-mono); font-size: 7pt; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--clay); display: block; margin-bottom: 2mm;
}
.pipeline .stage h4 { font-family: var(--font-display); font-size: 11pt; margin: 0 0 1.5mm 0; line-height: 1.15; }
.pipeline .stage p { font-size: 8pt; line-height: 1.4; color: var(--ink-90); margin: 0; }
.pipeline .stage::after {
  content: '›'; position: absolute; right: -3mm; top: 50%; transform: translateY(-50%);
  font-family: var(--font-display); font-size: 18pt; color: var(--ink-40);
  background: var(--paper); padding: 0 2pt; line-height: 1;
}
.pipeline .stage:last-child::after { content: none; }

/* TIMELINE */
.timeline {
  margin: 8mm 0; position: relative;
}
.timeline-track {
  position: relative; height: 14mm; background: var(--paper-soft);
  border: 1px solid var(--ink-12); border-radius: 2pt; overflow: hidden;
}
.timeline-track .seg {
  position: absolute; top: 0; bottom: 0; padding: 3mm 3mm; font-family: var(--font-mono);
  font-size: 7pt; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink);
  border-right: 1px solid var(--paper);
  display: flex; flex-direction: column; justify-content: center;
}
.timeline-axis {
  display: grid; grid-template-columns: repeat(17, 1fr); margin-top: 1.5mm;
  font-family: var(--font-mono); font-size: 6.5pt; letter-spacing: 0.14em; color: var(--ink-60);
}
.timeline-axis span { text-align: center; }

/* CONTACT */
.contact-card {
  border-top: 2pt solid var(--clay);
  background: var(--paper-soft);
  padding: 12mm 12mm 12mm 12mm;
  margin-top: 30mm;
}
.contact-card dl { display: grid; grid-template-columns: 50mm 1fr; gap: 4mm 8mm; margin: 0; }
.contact-card dt { font-family: var(--font-mono); font-size: 7.5pt; letter-spacing: 0.18em; text-transform: uppercase; color: var(--ink-60); }
.contact-card dd { font-family: var(--font-body); font-size: 11pt; color: var(--ink); margin: 0; font-weight: 500; }
.signoff {
  margin-top: 18mm; padding-top: 4mm; border-top: 1px solid var(--ink-12);
  font-family: var(--font-mono); font-size: 7.5pt; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--ink-60);
  display: flex; justify-content: space-between;
}

/* HEBREW SAMPLE TYPOGRAPHY */
.heb { font-family: 'Newsreader', 'David', 'Times New Roman', serif; direction: rtl; unicode-bidi: isolate; font-size: 14pt; }
.heb-big { font-family: 'Newsreader', 'David', 'Times New Roman', serif; direction: rtl; unicode-bidi: isolate; font-size: 22pt; }
.heb-mono { font-family: 'JetBrains Mono', 'David', monospace; direction: rtl; unicode-bidi: isolate; }

/* MARKDOWN STRIP */
.markdown-body, body.jishu-brief { background: var(--paper) !important; }
</style>

<!-- ========== SHEET 1 — COVER ========== -->
<section class="sheet cover">
  <div class="cover-inner">
    <div>
      <span class="cover-mark"><span style="font-family: var(--font-display); font-style: italic; font-weight:500;">Jishu</span><span class="dot"></span><span style="font-family: var(--font-mono); font-style: normal; font-size: 9pt; letter-spacing: 0.22em; text-transform: uppercase; color: var(--ink-60); margin-left: 6px;">tirvi · market brief</span></span>
    </div>
    <div>
      <div class="cover-eyebrow">Hebrew · Dyslexia · Accommodations · Israel</div>
      <h1 class="cover-title">Hebrew exam reading,<br/><em class="accent" style="font-style:italic; font-family: var(--font-display);">redesigned.</em></h1>
      <div class="cover-rule"></div>
      <p class="cover-lede">A reader for dyslexic Israeli students that&rsquo;s not human &mdash; but reads like one. The case for tirvi: the gap, the audience, and the architecture that closes it.</p>
    </div>
    <div>
      <dl class="cover-meta">
        <div><dt>Author</dt><dd>tirvi research</dd></div>
        <div><dt>Published</dt><dd>April 2026</dd></div>
        <div><dt>Status</dt><dd>v1.0 · current</dd></div>
      </dl>
    </div>
  </div>
</section>

<!-- ========== SHEET 2 — TOC ========== -->
<section class="sheet">
  <div class="bar-top">
    <span class="brand">Jishu<span class="dot"></span><span class="meta">tirvi · market brief</span></span>
    <span>v1.0</span>
  </div>
  <div class="bar-bot"><span>jishutech.io</span><span>02 / 10</span></div>
  <div style="margin-top: 6mm;">
    <div class="eyebrow">Contents</div>
    <h2 style="font-size: 32pt; line-height: 1.05;">Inside this brief.</h2>
    <p class="lede" style="margin-top: 4mm;">Seven sections, ten pages. Three numbers that decide if it works.</p>
  </div>
  <ol class="toc-list" style="margin-top: 12mm;">
    <li><span></span><span><span class="title">The Problem</span><span class="sub">Why generic Hebrew TTS breaks on exam content.</span></span><span class="pg">p. 03</span></li>
    <li><span></span><span><span class="title">Why Hebrew Is Hard</span><span class="sub">No vowels, heavy acronyms, RTL meets LTR.</span></span><span class="pg">p. 04</span></li>
    <li><span></span><span><span class="title">Market Size</span><span class="sub">The accommodation cohort, by the numbers.</span></span><span class="pg">p. 05</span></li>
    <li><span></span><span><span class="title">The Gap</span><span class="sub">Generic readers, generic results &mdash; a comparison.</span></span><span class="pg">p. 06</span></li>
    <li><span></span><span><span class="title">The Solution</span><span class="sub">Don&rsquo;t add TTS to OCR. Add a brain.</span></span><span class="pg">p. 07</span></li>
    <li><span></span><span><span class="title">The Moat</span><span class="sub">Five micro-stages between text and audio.</span></span><span class="pg">p. 08</span></li>
    <li><span></span><span><span class="title">Targets &amp; Plan</span><span class="sub">Three numbers, sixteen weeks, eleven epics.</span></span><span class="pg">p. 09</span></li>
  </ol>
</section>

<!-- ========== SHEET 3 — THE PROBLEM ========== -->
<section class="sheet">
  <div class="bar-top">
    <span class="brand">Jishu<span class="dot"></span><span class="meta">01 · The Problem</span></span>
    <span>v1.0</span>
  </div>
  <div class="bar-bot"><span>jishutech.io</span><span>03 / 10</span></div>
  <div class="eyebrow">01 / Problem</div>
  <h2 style="font-size: 30pt; line-height: 1.08; max-width: 145mm;">Hebrew exam reading is broken.</h2>
  <p class="lede" style="margin-top: 4mm; max-width: 150mm;">Israeli students with dyslexia are entitled to a human reader during exams. When the human is replaced by software, today&rsquo;s software fails them &mdash; not because Hebrew TTS is bad, but because no one wired Hebrew NLP into a reader that understands an exam.</p>

  <div class="grid-2-asym" style="margin-top: 10mm;">
    <div>
      <h3 style="margin-bottom: 4mm;">Three reasons today&rsquo;s tools don&rsquo;t work</h3>
      <ul style="font-size: 10.5pt; line-height: 1.55; padding-left: 4mm; margin: 0;">
        <li><b>Pronunciation guesses.</b> Hebrew is written without vowels. Generic TTS guesses, gets homographs wrong, and a dyslexic ear can&rsquo;t recover from the error.</li>
        <li><b>Flat reading.</b> Question stems, answer choices, table cells, math &mdash; all read top-to-bottom as one stream. A human reader re-reads the choices on demand. Software doesn&rsquo;t.</li>
        <li><b>No accommodation-grade UX.</b> No replay-this-sentence, no slow-this-word, no jump-to-question, no word-sync highlight. Public criticism of Israel&rsquo;s 2024 computerized-reading pilot says it directly.</li>
      </ul>
    </div>
    <div>
      <div class="pull">
        &ldquo;Cold, rigid, not adjustable in real time.&rdquo;
        <cite>Public criticism &mdash; Israeli MoE 2024 computerized-reading pilot for Bagrut math, replacing human readers for students with dyscalculia / dysgraphia. Ynet, 2024.</cite>
      </div>
    </div>
  </div>

  <div class="hero-stat">
    <div class="num">54<span style="font-size: 32pt; vertical-align: 0.25em; color: var(--clay);">%</span></div>
    <div class="lbl">of Israeli high-schoolers received Bagrut accommodations in 2021 &mdash; up from 35% in 2011. Level-1 accommodations alone jumped 8% &rarr; 40% (2016&ndash;2021).<span class="src">Taub Center, 2024 &middot; Bagrut Exam Accommodations</span></div>
  </div>
</section>

<!-- ========== SHEET 4 — WHY HEBREW IS HARD ========== -->
<section class="sheet">
  <div class="bar-top">
    <span class="brand">Jishu<span class="dot"></span><span class="meta">01.1 · The hidden hardness</span></span>
    <span>v1.0</span>
  </div>
  <div class="bar-bot"><span>jishutech.io</span><span>04 / 10</span></div>
  <div class="eyebrow">01.1 / Why Hebrew Is Hard</div>
  <h2 style="font-size: 28pt; line-height: 1.08; max-width: 165mm;">Three things English readers never face.</h2>
  <p class="lede" style="margin-top: 4mm; max-width: 165mm;">English TTS works because English on the page already encodes the pronunciation. Hebrew doesn&rsquo;t. The reader has to think before it can speak.</p>

  <!-- Big SVG: ספר branching to 3 pronunciations -->
  <div style="margin: 8mm 0 4mm 0; display: flex; justify-content: center;">
    <svg width="170mm" height="58mm" viewBox="0 0 480 165" xmlns="http://www.w3.org/2000/svg" style="font-family: var(--font-display);">
      <!-- center node -->
      <rect x="195" y="60" width="90" height="46" rx="4" fill="#F4ECE0" stroke="#2B211A" stroke-width="1.4"/>
      <text x="240" y="78" text-anchor="middle" font-size="9" font-family="JetBrains Mono" fill="#7B6E5E" letter-spacing="2">UNDIACRITIZED</text>
      <text x="240" y="100" text-anchor="middle" font-size="22" font-weight="500" fill="#2B211A" font-family="Newsreader, David, serif" direction="rtl">ספר</text>
      <!-- branches -->
      <line x1="200" y1="83" x2="80" y2="32" stroke="#C35A3A" stroke-width="1.4"/>
      <line x1="200" y1="83" x2="80" y2="83" stroke="#C35A3A" stroke-width="1.4"/>
      <line x1="200" y1="83" x2="80" y2="134" stroke="#C35A3A" stroke-width="1.4"/>
      <!-- option 1 -->
      <rect x="0" y="10" width="170" height="44" rx="3" fill="#FAF4EB" stroke="#E8A88F" stroke-width="1"/>
      <text x="12" y="26" font-size="7" font-family="JetBrains Mono" fill="#A64828" letter-spacing="2">SÉFER · NOUN</text>
      <text x="12" y="42" font-size="13" font-weight="500" fill="#2B211A" font-family="Newsreader, David, serif" direction="rtl">סֵפֶר</text>
      <text x="80" y="42" font-size="9" fill="#2B211A" font-style="italic" font-family="Newsreader, serif">— book</text>
      <!-- option 2 -->
      <rect x="0" y="61" width="170" height="44" rx="3" fill="#FAF4EB" stroke="#E8A88F" stroke-width="1"/>
      <text x="12" y="77" font-size="7" font-family="JetBrains Mono" fill="#A64828" letter-spacing="2">SAFÁR · VERB</text>
      <text x="12" y="93" font-size="13" font-weight="500" fill="#2B211A" font-family="Newsreader, David, serif" direction="rtl">סָפַר</text>
      <text x="80" y="93" font-size="9" fill="#2B211A" font-style="italic" font-family="Newsreader, serif">— he counted</text>
      <!-- option 3 -->
      <rect x="0" y="112" width="170" height="44" rx="3" fill="#FAF4EB" stroke="#E8A88F" stroke-width="1"/>
      <text x="12" y="128" font-size="7" font-family="JetBrains Mono" fill="#A64828" letter-spacing="2">SAPÉR · IMPER.</text>
      <text x="12" y="144" font-size="13" font-weight="500" fill="#2B211A" font-family="Newsreader, David, serif" direction="rtl">סַפֵּר</text>
      <text x="80" y="144" font-size="9" fill="#2B211A" font-style="italic" font-family="Newsreader, serif">— tell!</text>
      <!-- right side: context arrow -->
      <line x1="295" y1="83" x2="395" y2="83" stroke="#2B211A" stroke-width="1.4" marker-end="url(#arr)"/>
      <defs><marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#2B211A"/></marker></defs>
      <rect x="395" y="55" width="85" height="56" rx="3" fill="#F6E0D4" stroke="#C35A3A" stroke-width="1.4"/>
      <text x="437" y="73" text-anchor="middle" font-size="7" font-family="JetBrains Mono" fill="#A64828" letter-spacing="2">+ CONTEXT</text>
      <text x="437" y="92" text-anchor="middle" font-size="9.5" fill="#2B211A" font-family="Manrope, sans-serif">DictaBERT</text>
      <text x="437" y="105" text-anchor="middle" font-size="9.5" fill="#2B211A" font-family="Manrope, sans-serif">+ Nakdan</text>
    </svg>
  </div>

  <div class="grid-3" style="margin-top: 6mm;">
    <div class="card"><span class="num-mono">01 · No vowels</span><h3>Same letters, three readings.</h3><p>Hebrew omits ניקוד. <span class="heb">ספר</span> is book / counted / tell. Only morphology + context can choose. Generic TTS picks one and ships it.</p></div>
    <div class="card"><span class="num-mono">02 · Acronyms</span><h3>Heavy density, idiomatic expansion.</h3><p><span class="heb">ד״ר</span> &rarr; doctor, <span class="heb">עמ׳</span> &rarr; page, <span class="heb">מס׳</span> &rarr; number. Generic TTS spells them letter-by-letter. Hebrew exam content is full of them.</p></div>
    <div class="card"><span class="num-mono">03 · Mixed direction</span><h3>RTL meets LTR, mid-sentence.</h3><p>Bagrut math and English mix Hebrew with English, numbers, formulas. Google&rsquo;s SSML <code>&lt;lang&gt;</code> tag returns silence on Hebrew. One sentence, three scripts, no clean handover.</p></div>
  </div>
</section>

<!-- ========== SHEET 5 — MARKET SIZE ========== -->
<section class="sheet">
  <div class="bar-top">
    <span class="brand">Jishu<span class="dot"></span><span class="meta">02 · Market</span></span>
    <span>v1.0</span>
  </div>
  <div class="bar-bot"><span>jishutech.io</span><span>05 / 10</span></div>
  <div class="eyebrow">02 / Market Size</div>
  <h2 style="font-size: 28pt; line-height: 1.08;">The accommodation cohort,<br/>by the numbers.</h2>
  <p class="lede" style="max-width: 160mm; margin-top: 3mm;">Israel formally classifies more dyslexic students than almost any peer system, and the share is still rising.</p>

  <div class="kpi-row" style="margin-top: 10mm;">
    <div class="kpi">
      <span class="num">~500K</span>
      <span class="lbl">Israeli students estimated to have dyslexia &mdash; about three to five in every class of thirty.</span>
      <span class="src">Israel National News</span>
    </div>
    <div class="kpi ochre">
      <span class="num">54<small>%</small></span>
      <span class="lbl">of Israeli high-schoolers received Bagrut accommodations in 2021 &mdash; vs. ~15% international LD prevalence.</span>
      <span class="src">Taub Center · 2024</span>
    </div>
    <div class="kpi sage">
      <span class="num">+19<small>pp</small></span>
      <span class="lbl">growth in the accommodation rate over a decade (2011 &rarr; 2021), driven by Level-1 accommodations.</span>
      <span class="src">Taub Center · 2024</span>
    </div>
  </div>

  <!-- Bar chart SVG: accommodation rate growth -->
  <h3 style="margin: 10mm 0 4mm 0; font-size: 13pt;">Bagrut accommodations rate, Israeli high-schoolers</h3>
  <div style="display: flex; justify-content: center;">
    <svg width="170mm" height="58mm" viewBox="0 0 510 175" xmlns="http://www.w3.org/2000/svg">
      <!-- baseline -->
      <line x1="40" y1="150" x2="500" y2="150" stroke="#2B211A" stroke-width="1.2"/>
      <!-- y-axis ticks -->
      <text x="32" y="153" text-anchor="end" font-size="8" font-family="JetBrains Mono" fill="#7B6E5E">0</text>
      <text x="32" y="115" text-anchor="end" font-size="8" font-family="JetBrains Mono" fill="#7B6E5E">20</text>
      <text x="32" y="80" text-anchor="end" font-size="8" font-family="JetBrains Mono" fill="#7B6E5E">40</text>
      <text x="32" y="45" text-anchor="end" font-size="8" font-family="JetBrains Mono" fill="#7B6E5E">60%</text>
      <line x1="40" y1="115" x2="500" y2="115" stroke="#E0D4C0" stroke-width="0.6" stroke-dasharray="2 2"/>
      <line x1="40" y1="80" x2="500" y2="80" stroke="#E0D4C0" stroke-width="0.6" stroke-dasharray="2 2"/>
      <line x1="40" y1="45" x2="500" y2="45" stroke="#E0D4C0" stroke-width="0.6" stroke-dasharray="2 2"/>
      <!-- bars: 2011 35%, 2016 ~45%, 2021 54%; 1% = 1.75 px (60% = 105px) -->
      <!-- 2011: 35% = 61px -->
      <rect x="80" y="89" width="80" height="61" fill="#EAE0D0" stroke="#A64828" stroke-width="0.8"/>
      <text x="120" y="84" text-anchor="middle" font-size="11" font-family="Newsreader, serif" font-weight="500" fill="#2B211A">35%</text>
      <text x="120" y="166" text-anchor="middle" font-size="9" font-family="JetBrains Mono" fill="#7B6E5E" letter-spacing="2">2011</text>
      <!-- 2016: 45% = 79px (intermediate, MoE Level-1 expansion era) -->
      <rect x="220" y="71" width="80" height="79" fill="#E8A88F" stroke="#A64828" stroke-width="0.8"/>
      <text x="260" y="66" text-anchor="middle" font-size="11" font-family="Newsreader, serif" font-weight="500" fill="#2B211A">~45%</text>
      <text x="260" y="166" text-anchor="middle" font-size="9" font-family="JetBrains Mono" fill="#7B6E5E" letter-spacing="2">2016</text>
      <!-- 2021: 54% = 95px -->
      <rect x="360" y="55" width="80" height="95" fill="#C35A3A" stroke="#A64828" stroke-width="0.8"/>
      <text x="400" y="50" text-anchor="middle" font-size="11" font-family="Newsreader, serif" font-weight="500" fill="#2B211A">54%</text>
      <text x="400" y="166" text-anchor="middle" font-size="9" font-family="JetBrains Mono" fill="#7B6E5E" letter-spacing="2">2021</text>
      <!-- arrow showing growth -->
      <line x1="160" y1="89" x2="350" y2="60" stroke="#A64828" stroke-width="1.2" stroke-dasharray="3 2" marker-end="url(#arr2)"/>
      <defs><marker id="arr2" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#A64828"/></marker></defs>
      <text x="500" y="85" text-anchor="end" font-size="10" font-family="Newsreader, serif" font-style="italic" fill="#A64828">+19pp</text>
      <text x="500" y="100" text-anchor="end" font-size="7" font-family="JetBrains Mono" fill="#7B6E5E" letter-spacing="1.6">10-YEAR DELTA</text>
    </svg>
  </div>
  <p class="tiny muted" style="text-align: center; margin-top: 1mm; font-family: var(--font-mono); letter-spacing: 0.14em;">SOURCE · TAUB CENTER 2024 · BAGRUT EXAM ACCOMMODATIONS</p>
</section>

<!-- ========== SHEET 6 — THE GAP ========== -->
<section class="sheet">
  <div class="bar-top">
    <span class="brand">Jishu<span class="dot"></span><span class="meta">02.1 · The Gap</span></span>
    <span>v1.0</span>
  </div>
  <div class="bar-bot"><span>jishutech.io</span><span>06 / 10</span></div>
  <div class="eyebrow">02.1 / Existing Tools</div>
  <h2 style="font-size: 28pt; line-height: 1.08;">Generic readers, generic results.</h2>
  <p class="lede" style="max-width: 160mm; margin-top: 3mm;">No commercial product today combines Hebrew OCR, Hebrew NLP, and Hebrew TTS into an exam-shaped reader. The building blocks exist. No one has wired them together.</p>

  <table class="cmp" style="margin-top: 8mm;">
    <thead><tr>
      <th style="width: 38mm;">Tool</th>
      <th>Hebrew TTS</th>
      <th>Exam structure</th>
      <th>Diacritization</th>
      <th>Word-sync</th>
      <th>Verdict</th>
    </tr></thead>
    <tbody>
      <tr><td>ElevenLabs (v3, Flash v2.5)</td><td><span class="dot-full"></span></td><td><span class="dot-none"></span></td><td><span class="dot-none"></span></td><td><span class="dot-full"></span></td><td>Generic API</td></tr>
      <tr><td>Speechify</td><td><span class="dot-full"></span></td><td><span class="dot-none"></span></td><td><span class="dot-none"></span></td><td><span class="dot-full"></span></td><td>Generic article reader</td></tr>
      <tr><td>NaturalReader</td><td><span class="dot-full"></span></td><td><span class="dot-none"></span></td><td><span class="dot-none"></span></td><td><span class="dot-half"></span></td><td>Generic doc TTS</td></tr>
      <tr><td>Voice Dream Scanner</td><td><span class="dot-none"></span></td><td><span class="dot-half"></span></td><td><span class="dot-none"></span></td><td><span class="dot-full"></span></td><td>Hebrew not supported</td></tr>
      <tr><td>Kurzweil 3000</td><td><span class="dot-none"></span></td><td><span class="dot-full"></span></td><td><span class="dot-none"></span></td><td><span class="dot-full"></span></td><td>No Hebrew voice</td></tr>
      <tr><td>MS Immersive Reader</td><td><span class="dot-half"></span></td><td><span class="dot-half"></span></td><td><span class="dot-none"></span></td><td><span class="dot-half"></span></td><td>RTL layout issues</td></tr>
      <tr><td>Read&amp;Write (Texthelp)</td><td><span class="dot-none"></span></td><td><span class="dot-half"></span></td><td><span class="dot-none"></span></td><td><span class="dot-full"></span></td><td>No first-class Hebrew</td></tr>
      <tr><td>Israeli MoE 2024 pilot</td><td><span class="dot-full"></span></td><td><span class="dot-none"></span></td><td><span class="dot-half"></span></td><td><span class="dot-none"></span></td><td>&ldquo;Cold, rigid, not adjustable&rdquo;</td></tr>
      <tr class="tirvi"><td>tirvi</td><td><span class="dot-full"></span></td><td><span class="dot-full"></span></td><td><span class="dot-full"></span></td><td><span class="dot-full"></span></td><td>Built for Hebrew exams</td></tr>
    </tbody>
  </table>
  <div class="legend">
    <span><span class="dot-full"></span> &nbsp; Full support</span>
    <span><span class="dot-half"></span> &nbsp; Partial / limited</span>
    <span><span class="dot-none"></span> &nbsp; None</span>
  </div>

  <p style="margin-top: 6mm; max-width: 175mm; font-family: var(--font-display); font-style: italic; font-size: 11pt; line-height: 1.5; color: var(--ink-90);">The building blocks &mdash; DictaBERT, Dicta-Nakdan, Phonikud, Google he-IL TTS &mdash; all exist. No one has assembled them into a vertically integrated reader for exam content. <span class="mono" style="font-style: normal; font-size: 7.5pt; letter-spacing: 0.16em; text-transform: uppercase; color: var(--ink-60); margin-left: 4mm;">&mdash; tirvi research synthesis &middot; april 2026</span></p>
</section>

<!-- ========== SHEET 7 — THE SOLUTION ========== -->
<section class="sheet">
  <div class="bar-top">
    <span class="brand">Jishu<span class="dot"></span><span class="meta">03 · The Solution</span></span>
    <span>v1.0</span>
  </div>
  <div class="bar-bot"><span>jishutech.io</span><span>07 / 10</span></div>
  <div class="eyebrow">03 / Solution</div>
  <h2 style="font-size: 30pt; line-height: 1.08;">Don&rsquo;t add TTS to OCR.<br/><em class="accent" style="font-style: italic;">Add a brain.</em></h2>
  <p class="lede" style="max-width: 165mm; margin-top: 3mm;">The defensible layer is the middle stage &mdash; Hebrew morphology, disambiguation, diacritization, and reading-plan shaping. OCR and TTS are commodities behind adapters.</p>

  <div class="pipeline" style="margin-top: 12mm;">
    <div class="stage">
      <span class="num-mono">01 · Ingest</span>
      <h4>Hebrew OCR</h4>
      <p>Tesseract <code style="font-family: var(--font-mono); font-size: 8pt;">heb</code> default, Document AI fallback, DeepSeek-OCR pilot. Structured blocks + bboxes, not flat text.</p>
    </div>
    <div class="stage moat">
      <span class="num-mono">02 · Interpret &mdash; the moat</span>
      <h4>Hebrew NLP</h4>
      <p>DictaBERT for morphology &amp; disambiguation. Dicta-Nakdan for ניקוד. Phonikud for stress + IPA G2P.</p>
    </div>
    <div class="stage moat">
      <span class="num-mono">03 · Shape</span>
      <h4>Reading Plan</h4>
      <p>Per-block JSON: tokens, lemma, POS, pronunciation hints, SSML cues, structural type (question / answer / table).</p>
    </div>
    <div class="stage">
      <span class="num-mono">04 · Voice</span>
      <h4>Hebrew TTS</h4>
      <p>Google Wavenet for word-sync; Chirp 3 HD for continuous; Azure as alternate. Cached by content hash.</p>
    </div>
    <div class="stage">
      <span class="num-mono">05 · Listen</span>
      <h4>Player</h4>
      <p>Side-by-side viewer, word-sync highlight, per-block playback, repeat sentence, font-size, WCAG 2.2 AA.</p>
    </div>
  </div>

  <div style="margin-top: 10mm; display: grid; grid-template-columns: 1fr 1fr; gap: 10mm;">
    <div>
      <h3 style="font-size: 13pt; margin-bottom: 3mm;">The three principles that decide it</h3>
      <ul style="font-size: 10pt; line-height: 1.55; padding-left: 4mm; margin: 0;">
        <li><b>The reading plan is the product.</b> 3&times; as much code in the interpretation layer as in adapters.</li>
        <li><b>Adapters return rich result objects, not bytes.</b> Timepoints, bboxes, confidences survive the port boundary.</li>
        <li><b>Cache by content hash, share across users.</b> The single biggest cost lever and the only way the $0.02 / page target survives premium voices.</li>
      </ul>
    </div>
    <div>
      <h3 style="font-size: 13pt; margin-bottom: 3mm;">Why now</h3>
      <ul style="font-size: 10pt; line-height: 1.55; padding-left: 4mm; margin: 0;">
        <li><b>2024 MoE pilot</b> proved the policy direction (digital readers) and the UX gap (cold, rigid).</li>
        <li><b>Dicta lineage</b> (Bar-Ilan) shipped DictaBERT 2.0 in 2024 &mdash; SOTA on UD-Hebrew.</li>
        <li><b>Phonikud</b> (June 2025) gives real-time Hebrew G2P with stress &amp; vocal shva &mdash; the missing layer.</li>
        <li><b>Google Chirp 3 HD he-IL</b> shipped in 2025 &mdash; premium voice quality at last.</li>
      </ul>
    </div>
  </div>
</section>

<!-- ========== SHEET 8 — THE MOAT ========== -->
<section class="sheet">
  <div class="bar-top">
    <span class="brand">Jishu<span class="dot"></span><span class="meta">03.1 · The Moat</span></span>
    <span>v1.0</span>
  </div>
  <div class="bar-bot"><span>jishutech.io</span><span>08 / 10</span></div>
  <div class="eyebrow">03.1 / The moat &mdash; Hebrew Reading Plan</div>
  <h2 style="font-size: 26pt; line-height: 1.08;">Five micro-stages between text and audio.</h2>
  <p class="lede" style="max-width: 165mm; margin-top: 3mm;">This is where context-aware Hebrew reading happens &mdash; morphological disambiguation, pronunciation prediction, exam-domain adaptation. The academic framing matches the engineering one.</p>

  <!-- Five horizontal stage cards, slim -->
  <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 4mm; margin-top: 8mm;">
    <div class="card" style="padding: 4mm;"><span class="num-mono" style="font-size: 7pt;">01 · Tokenize</span><h3 style="font-size: 11pt;">Morphology</h3><p style="font-size: 8pt; line-height: 1.4;">DictaBERT-large-joint &mdash; segmentation, POS, lemma, dependency. SOTA on UD-Hebrew 2024&ndash;25.</p></div>
    <div class="card" style="padding: 4mm;"><span class="num-mono" style="font-size: 7pt;">02 · Disambiguate</span><h3 style="font-size: 11pt;">Context</h3><p style="font-size: 8pt; line-height: 1.4;">Sentence context picks the right reading for homographs. <span class="heb-mono" style="font-size: 9pt;">ספר</span> &rarr; verb or noun?</p></div>
    <div class="card" style="padding: 4mm; background: var(--clay-wash); border-color: var(--clay-soft); border-top: 3pt solid var(--clay);"><span class="num-mono" style="font-size: 7pt;">03 · Diacritize</span><h3 style="font-size: 11pt;">Add ניקוד</h3><p style="font-size: 8pt; line-height: 1.4;">Dicta-Nakdan adds vowels for ambiguous tokens. ~86.86% word-level accuracy.</p></div>
    <div class="card" style="padding: 4mm; background: var(--clay-wash); border-color: var(--clay-soft); border-top: 3pt solid var(--clay);"><span class="num-mono" style="font-size: 7pt;">04 · G2P</span><h3 style="font-size: 11pt;">Phonemes</h3><p style="font-size: 8pt; line-height: 1.4;">Phonikud (June 2025) outputs IPA with stress and vocal shva. Real-time, plug into any TTS.</p></div>
    <div class="card" style="padding: 4mm;"><span class="num-mono" style="font-size: 7pt;">05 · Shape</span><h3 style="font-size: 11pt;">SSML</h3><p style="font-size: 8pt; line-height: 1.4;">Breaks between answers, emphasis on question numbers, language switch on English spans, mark for word-sync.</p></div>
  </div>

  <!-- Worked example -->
  <h3 style="margin: 12mm 0 4mm 0; font-size: 13pt;">Worked example &mdash; one Bagrut question stem</h3>
  <div style="background: var(--paper-soft); border: 1px solid var(--ink-12); padding: 6mm 8mm;">
    <div style="display: grid; grid-template-columns: 36mm 1fr; gap: 4mm 6mm; align-items: baseline;">
      <div class="num-mono" style="color: var(--ink-60); font-size: 7.5pt;">INPUT</div>
      <div><span class="heb-big" style="color: var(--ink);">ספר את הסיפור במילים שלך.</span></div>
      <div class="num-mono" style="color: var(--ink-60); font-size: 7.5pt;">DISAMBIGUATED</div>
      <div><span class="heb-big" style="color: var(--ink);">סַפֵּר אֶת הַסִּיפּוּר בְּמִלִּים שֶׁלָּךְ.</span> <span class="muted" style="font-family: var(--font-display); font-style: italic; font-size: 11pt;">&mdash; "tell the story in your own words" (verb sapér, not noun séfer)</span></div>
      <div class="num-mono" style="color: var(--ink-60); font-size: 7.5pt;">SSML</div>
      <div style="font-family: var(--font-mono); font-size: 8.5pt; line-height: 1.5; color: var(--clay-deep);">&lt;mark name="q4-w0"/&gt;&lt;emphasis level="moderate"&gt;<span style="font-family: 'Newsreader', serif; font-size: 11pt; color: var(--ink);" class="heb">סַפֵּר</span>&lt;/emphasis&gt; <span style="font-family: 'Newsreader', serif; font-size: 11pt; color: var(--ink);" class="heb">אֶת הַסִּיפּוּר</span> &lt;break time="200ms"/&gt; <span style="font-family: 'Newsreader', serif; font-size: 11pt; color: var(--ink);" class="heb">בְּמִלִּים שֶׁלָּךְ</span>.</div>
      <div class="num-mono" style="color: var(--ink-60); font-size: 7.5pt;">SPOKEN</div>
      <div style="font-family: var(--font-display); font-style: italic; font-size: 12pt; color: var(--ink);">"sa<b>pér</b> et ha-sipúr be-milím shelákh"</div>
    </div>
  </div>
</section>

<!-- ========== SHEET 9 — TARGETS + PLAN ========== -->
<section class="sheet">
  <div class="bar-top">
    <span class="brand">Jishu<span class="dot"></span><span class="meta">04 · Targets &amp; Plan</span></span>
    <span>v1.0</span>
  </div>
  <div class="bar-bot"><span>jishutech.io</span><span>09 / 10</span></div>
  <div class="eyebrow">04 / Targets &amp; Plan</div>
  <h2 style="font-size: 28pt; line-height: 1.08;">Three numbers,<br/>sixteen weeks.</h2>

  <div class="kpi-row" style="margin-top: 8mm;">
    <div class="kpi">
      <span class="num">&ge;90<small>%</small></span>
      <span class="lbl">word-pronunciation accuracy on the tirvi-Hebrew-Exam Benchmark v0.</span>
      <span class="src">Validated by blind MOS · n=10 dyslexic teens</span>
    </div>
    <div class="kpi ochre">
      <span class="num">&le;30s</span>
      <span class="lbl">time to first audio, p50, on a 5-page scanned exam.</span>
      <span class="src">Cloud Run min-instances=1 · cpu-boost</span>
    </div>
    <div class="kpi sage">
      <span class="num">&le;$0.02</span>
      <span class="lbl">amortized cost per processed page across a 30-day window.</span>
      <span class="src">Wavenet + content-hash cache &gt; 25%</span>
    </div>
  </div>

  <h3 style="margin: 12mm 0 4mm 0; font-size: 13pt;">Sixteen-week MVP &mdash; 11 epics, six phases, practice-mode framing</h3>

  <!-- Timeline SVG -->
  <div style="display: flex; justify-content: center; margin: 4mm 0 2mm 0;">
    <svg width="180mm" height="48mm" viewBox="0 0 540 145" xmlns="http://www.w3.org/2000/svg">
      <rect x="20" y="44" width="500" height="36" fill="#FAF4EB" stroke="#E0D4C0" stroke-width="0.6"/>
      <rect x="20" y="44" width="32" height="36" fill="#EAE0D0"/>
      <rect x="52" y="44" width="93" height="36" fill="#DDE3D4"/>
      <rect x="145" y="44" width="156" height="36" fill="#C35A3A"/>
      <rect x="301" y="44" width="93" height="36" fill="#F4E6CC"/>
      <rect x="301" y="80" width="125" height="14" fill="#E8A88F" opacity="0.85"/>
      <rect x="394" y="44" width="93" height="36" fill="#F6E0D4"/>
      <text x="36" y="65" font-family="JetBrains Mono" font-size="6.2" letter-spacing="1.3" fill="#2B211A" text-anchor="middle">P0</text>
      <text x="36" y="74" font-family="Manrope" font-size="6" fill="#2B211A" text-anchor="middle">DevX</text>
      <text x="98" y="59" font-family="JetBrains Mono" font-size="6.2" letter-spacing="1.3" fill="#2B211A" text-anchor="middle">P1</text>
      <text x="98" y="69" font-family="Manrope" font-size="7" fill="#2B211A" text-anchor="middle">Ingest</text>
      <text x="98" y="77" font-family="Manrope" font-size="6.5" fill="#2B211A" text-anchor="middle">+ OCR</text>
      <text x="223" y="58" font-family="JetBrains Mono" font-size="7" letter-spacing="1.4" fill="#FAF4EB" text-anchor="middle">P2 · THE MOAT</text>
      <text x="223" y="68" font-family="Newsreader, serif" font-style="italic" font-size="8" fill="#FAF4EB" text-anchor="middle">Hebrew Interpretation</text>
      <text x="223" y="76" font-family="Manrope" font-size="6.4" fill="#FAF4EB" text-anchor="middle">DictaBERT · Nakdan · Phonikud · Reading Plan</text>
      <text x="347" y="58" font-family="JetBrains Mono" font-size="6.2" letter-spacing="1.3" fill="#2B211A" text-anchor="middle">P3</text>
      <text x="347" y="68" font-family="Manrope" font-size="7" fill="#2B211A" text-anchor="middle">TTS +</text>
      <text x="347" y="76" font-family="Manrope" font-size="6.5" fill="#2B211A" text-anchor="middle">word-sync</text>
      <text x="363" y="91" font-family="JetBrains Mono" font-size="5.5" letter-spacing="1.2" fill="#A64828" text-anchor="middle">P4 · PLAYER (PARALLEL)</text>
      <text x="440" y="58" font-family="JetBrains Mono" font-size="6.2" letter-spacing="1.3" fill="#2B211A" text-anchor="middle">P5</text>
      <text x="440" y="68" font-family="Manrope" font-size="7" fill="#2B211A" text-anchor="middle">Quality</text>
      <text x="440" y="76" font-family="Manrope" font-size="6.5" fill="#2B211A" text-anchor="middle">+ Privacy</text>
      <line x1="20" y1="105" x2="520" y2="105" stroke="#2B211A" stroke-width="0.8"/>
      <text x="20" y="119" font-family="JetBrains Mono" font-size="7" fill="#7B6E5E">w0</text>
      <text x="145" y="119" font-family="JetBrains Mono" font-size="7" fill="#7B6E5E">w4</text>
      <text x="270" y="119" font-family="JetBrains Mono" font-size="7" fill="#7B6E5E">w8</text>
      <text x="395" y="119" font-family="JetBrains Mono" font-size="7" fill="#7B6E5E">w12</text>
      <text x="510" y="119" font-family="JetBrains Mono" font-size="7" fill="#7B6E5E" text-anchor="end">w16</text>
      <text x="20" y="32" font-family="JetBrains Mono" font-size="7" letter-spacing="1.6" fill="#A64828">PHASE TIMELINE · 16 WEEKS</text>
      <polygon points="510,40 514,44 510,48 506,44" fill="#C35A3A"/>
      <text x="510" y="38" font-family="Newsreader, serif" font-style="italic" font-size="7" fill="#A64828" text-anchor="middle">v1</text>
      <text x="20" y="138" font-family="JetBrains Mono" font-size="6.2" letter-spacing="1.3" fill="#7B6E5E">PRACTICE-AND-PREP FIRST · REAL-BAGRUT AS V2 AFTER MOE PILOT</text>
    </svg>
  </div>

  <p class="muted tiny" style="margin-top: 6mm; font-size: 8.5pt; line-height: 1.55; max-width: 175mm;"><b>Out of MVP scope, deferred to v1.1 / v2:</b> handwriting OCR, user accounts (move to small Cloud SQL), real-time WebSocket status, custom voices, math/SRE Hebrew localization, MoE pilot toward in-Bagrut use, mobile-native apps. <b>Privacy posture:</b> 24-hour default TTL, DPIA + parental-consent ≥14, upload attestation against third-party copyright.</p>
</section>

<!-- ========== SHEET 10 — CONTACT ========== -->
<section class="sheet">
  <div class="bar-top">
    <span class="brand">Jishu<span class="dot"></span><span class="meta">Contact</span></span>
    <span>v1.0</span>
  </div>
  <div class="bar-bot"><span>jishutech.io</span><span>10 / 10</span></div>
  <div class="eyebrow">End matter</div>
  <h2 style="font-size: 32pt; line-height: 1.05;">Where this brief goes next.</h2>
  <p class="lede" style="max-width: 165mm; margin-top: 3mm;">Three concrete moves on the desk: a benchmark, an ADR, and an outreach email.</p>

  <div class="contact-card">
    <dl>
      <dt>Document</dt><dd>tirvi · Market Brief · v1.0</dd>
      <dt>Source synthesis</dt><dd>docs/research/tirvi-validation-and-mvp-scoping.md</dd>
      <dt>Repository</dt><dd>VSProjects/tirvi</dd>
      <dt>Open ADRs</dt><dd>10 queued · TTS routing, NLP backbone, MVP framing, TTL, OCR primary, &hellip;</dd>
      <dt>Academic candidates</dt><dd>Bar-Ilan ONLP Lab (Tsarfaty) · Dicta · HUJI adiyoss-lab</dd>
      <dt>First three moves</dt><dd>1. Stand up tirvi-bench v0 &middot; 2. Run <code style="font-family: var(--font-mono); font-size: 9pt;">@design-pipeline</code> on ADR-006 (MVP framing) &middot; 3. Send the Bar-Ilan / Dicta / HUJI outreach</dd>
    </dl>
    <div class="signoff"><span>tirvi · April 2026 · v1.0</span><span>jishutech.io</span></div>
  </div>
</section>
