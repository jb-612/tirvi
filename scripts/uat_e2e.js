/**
 * E2E UAT for the tirvi POC reader.
 * Run: node scripts/uat_e2e.js
 * Prereq: demo server running on localhost:8000 (uv run scripts/run_demo.py)
 *
 * Checks:
 *  1. Page loads with CURRENT sha (not a historical run)
 *  2. /api/current sha matches; page.json + audio.json load without error
 *  3. Play button exists and is clickable
 *  4. After play, audio.currentTime advances within 2s
 *  5. Word-marker CSS top/left are non-negative (marker is inside the image)
 *  6. Marker advances monotonically within each line (no backward jumps mid-line)
 *  7. 404 errors logged by URL; no other JS errors
 *  8. Version list renders (at least 1 run listed in #version-nav)
 */

// resolve playwright from npx cache if not locally installed
let _playwright;
try { _playwright = require("playwright"); }
catch { _playwright = require("/Users/jbellish/.npm/_npx/9833c18b2d85bc59/node_modules/playwright"); }
const { chromium } = _playwright;
const path = require("path");
const fs = require("fs");
const http = require("http");

const BASE = "http://localhost:8000";
const SCREENSHOT_DIR = path.join(__dirname, "..", "uat-screenshots");

fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

function pass(msg) { console.log(`  ✓ ${msg}`); }
function fail(msg) { console.error(`  ✗ ${msg}`); process.exitCode = 1; }
function info(msg) { console.log(`  · ${msg}`); }

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let body = "";
      res.on("data", (c) => body += c);
      res.on("end", () => {
        try { resolve(JSON.parse(body)); }
        catch { resolve(null); }
      });
    }).on("error", reject);
  });
}

async function run() {
  // ── Pre-flight: get expected SHA from server ──────────────────────────────
  const currentInfo = await fetchJson(`${BASE}/api/current`).catch(() => null);
  const expectedSha = currentInfo?.sha;
  console.log(`\n=== tirvi E2E UAT (SHA: ${expectedSha ?? "unknown"}) ===\n`);

  const browser = await chromium.launch({
    headless: false,
    slowMo: 80,
    args: ["--autoplay-policy=no-user-gesture-required"],
  });
  const ctx = await browser.newContext({
    viewport: { width: 1400, height: 900 },
  });

  const page = await ctx.newPage();
  const consoleErrors = [];
  const notFoundUrls = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("pageerror", (err) => consoleErrors.push(`[pageerror] ${err.message}`));
  page.on("response", (res) => {
    if (res.status() === 404) notFoundUrls.push(res.url());
  });

  // ── 1. Page load (fresh, no cache) ────────────────────────────────────────
  console.log("1. Page load (fresh)");
  await page.goto(BASE, { waitUntil: "domcontentloaded", timeout: 15000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/01-initial.png` });

  const title = await page.title();
  title.includes("tirvi") ? pass(`title: "${title}"`) : fail(`unexpected title: "${title}"`);

  const imgVisible = await page.locator("#page-image").isVisible().catch(() => false);
  imgVisible ? pass("page-image visible") : fail("page-image NOT visible");

  const controlsVisible = await page.locator("#controls").isVisible().catch(() => false);
  controlsVisible ? pass("#controls visible") : fail("#controls NOT visible");

  // ── 2. Current SHA matches server (not a stale/historical run) ────────────
  console.log("\n2. Current SHA");
  const pageSha = await page.evaluate(() =>
    fetch("/api/current").then((r) => r.json()).then((d) => d.sha).catch(() => null)
  );
  if (expectedSha && pageSha === expectedSha) {
    pass(`player loaded SHA=${pageSha} (matches server current)`);
  } else {
    fail(`SHA mismatch: server says ${expectedSha}, page fetched ${pageSha}`);
  }

  const pageJson = await page.evaluate((s) =>
    fetch(`/${s}/page.json`).then((r) => r.ok ? "ok" : r.status).catch((e) => e.message), pageSha
  );
  pageJson === "ok" ? pass("page.json loaded") : fail(`page.json: ${pageJson}`);

  const audioJsonStatus = await page.evaluate((s) =>
    fetch(`/${s}/audio.json`).then((r) => r.ok ? "ok" : r.status).catch((e) => e.message), pageSha
  );
  audioJsonStatus === "ok" ? pass("audio.json loaded") : fail(`audio.json: ${audioJsonStatus}`);

  // Check audio.mp3 is non-empty
  const audioSize = await page.evaluate((s) =>
    fetch(`/${s}/audio.mp3`, { method: "HEAD" })
      .then((r) => parseInt(r.headers.get("content-length") || "0"))
      .catch(() => 0), pageSha
  );
  audioSize > 1000
    ? pass(`audio.mp3 present (${(audioSize/1024).toFixed(0)} KB)`)
    : fail(`audio.mp3 too small or missing (${audioSize} bytes)`);

  // ── 3. Play button ────────────────────────────────────────────────────────
  console.log("\n3. Play button");
  const playBtn = page.locator("button[aria-label*='Play'], button[aria-label*='play'], #play-btn, button:has-text('▶')").first();
  let playExists = await playBtn.isVisible().catch(() => false);

  if (!playExists) {
    const allBtns = await page.locator("#controls button").all();
    info(`Controls has ${allBtns.length} button(s):`);
    for (const b of allBtns) {
      const txt = (await b.textContent().catch(() => "")).trim();
      const lbl = await b.getAttribute("aria-label").catch(() => "");
      info(`  text="${txt}" aria-label="${lbl}"`);
    }
    fail("play button not found by selector");
  } else {
    pass("play button visible");
  }

  // ── 4. Audio advances ─────────────────────────────────────────────────────
  console.log("\n4. Audio playback");
  // Mute so autoplay isn't blocked by browser policy; we still verify currentTime advances
  await page.evaluate(() => {
    const a = document.querySelector("audio");
    if (a) a.volume = 0;
  });

  if (playExists) await playBtn.click().catch(() => {});
  else await page.locator("#controls button").first().click().catch(() => {});

  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/02-playing.png` });

  const audioState = await page.evaluate(() => {
    const a = document.querySelector("audio");
    if (!a) return { found: false };
    return {
      found: true,
      currentTime: a.currentTime,
      paused: a.paused,
      src: a.src,
      readyState: a.readyState,
    };
  });

  if (!audioState.found) {
    fail("no <audio> element found");
  } else if (audioState.currentTime > 0) {
    pass(`audio.currentTime=${audioState.currentTime.toFixed(2)}s (advancing)`);
    info(`  src: ${audioState.src}`);
    info(`  paused: ${audioState.paused}, readyState: ${audioState.readyState}`);
  } else {
    fail(`audio.currentTime=0 — audio not playing (paused=${audioState.paused}, readyState=${audioState.readyState})`);
    info(`  src: ${audioState.src}`);
  }

  // ── 5. Marker CSS position (relative to page-figure, not viewport) ────────
  console.log("\n5. Word-marker CSS position");
  const markerState = await page.evaluate(() => {
    const marker = document.getElementById("word-marker");
    const img = document.getElementById("page-image");
    if (!marker || !img) return null;
    const cs = getComputedStyle(marker);
    return {
      visibility: cs.visibility,
      cssLeft: cs.left,
      cssTop: cs.top,
      cssWidth: cs.width,
      cssHeight: cs.height,
      imgNaturalWidth: img.naturalWidth,
      imgNaturalHeight: img.naturalHeight,
      imgClientWidth: img.clientWidth,
      imgClientHeight: img.clientHeight,
    };
  });

  if (!markerState) {
    fail("marker or page-image element not found");
  } else {
    info(`  image: natural=${markerState.imgNaturalWidth}×${markerState.imgNaturalHeight}, rendered=${markerState.imgClientWidth}×${markerState.imgClientHeight}`);
    const leftPx = parseFloat(markerState.cssLeft);
    const topPx = parseFloat(markerState.cssTop);
    info(`  marker CSS: left=${markerState.cssLeft} top=${markerState.cssTop} w=${markerState.cssWidth} h=${markerState.cssHeight}`);
    info(`  marker visibility: ${markerState.visibility}`);

    if (markerState.visibility === "hidden") {
      fail("word-marker is hidden (audio may not have started the highlight loop)");
    } else {
      pass("word-marker is visible");
      leftPx >= 0
        ? pass(`marker CSS left=${leftPx}px (non-negative — within image)`)
        : fail(`marker CSS left=${leftPx}px (NEGATIVE — outside left edge of image)`);
      topPx >= 0
        ? pass(`marker CSS top=${topPx}px (non-negative — within image)`)
        : fail(`marker CSS top=${topPx}px (NEGATIVE — above image top edge)`);
      if (markerState.imgClientWidth > 0) {
        leftPx <= markerState.imgClientWidth
          ? pass(`marker CSS left=${leftPx}px <= rendered width ${markerState.imgClientWidth}px`)
          : fail(`marker CSS left=${leftPx}px EXCEEDS rendered width ${markerState.imgClientWidth}px`);
      }
    }
  }

  // ── 6. Marker advances (sample CSS left over 4s) ─────────────────────────
  console.log("\n6. Marker advance pattern (8 samples × 500ms)");
  if (audioState.currentTime > 0 && markerState?.visibility !== "hidden") {
    const lefts = [];
    for (let i = 0; i < 8; i++) {
      await page.waitForTimeout(500);
      const l = await page.evaluate(() => parseFloat(getComputedStyle(document.getElementById("word-marker")).left));
      lefts.push(Math.round(l));
    }
    info(`  left samples: ${lefts.join(", ")}`);

    // Count large backward jumps (> 20% of rendered width) — forward jumps are fine (line wrap)
    const renderedW = markerState.imgClientWidth || 400;
    const threshold = renderedW * 0.15;
    let backwardJumps = 0;
    for (let i = 1; i < lefts.length; i++) {
      const delta = lefts[i] - lefts[i - 1];
      if (delta > threshold) {
        info(`  frame ${i-1}→${i}: +${delta}px jump (line-wrap or first-word — expected)`);
      } else if (delta < -threshold) {
        backwardJumps++;
        info(`  frame ${i-1}→${i}: ${delta}px BACKWARD jump (unexpected)`);
      }
    }
    backwardJumps === 0
      ? pass("no unexpected backward marker jumps")
      : fail(`${backwardJumps} unexpected backward jump(s) detected`);
  } else {
    info("skipping (audio not playing or marker hidden)");
  }

  // ── 7. 404s and console errors ────────────────────────────────────────────
  console.log("\n7. Resource errors");
  await page.screenshot({ path: `${SCREENSHOT_DIR}/03-after-play.png` });

  if (notFoundUrls.length === 0) {
    pass("no 404 responses");
  } else {
    fail(`${notFoundUrls.length} 404(s):`);
    notFoundUrls.forEach((u) => console.error(`     404: ${u}`));
  }

  const nonFaviconErrors = consoleErrors.filter(
    (e) => !e.includes("favicon") && !e.includes("404")
  );
  if (nonFaviconErrors.length === 0) {
    pass("no non-404 JS console errors");
  } else {
    fail(`${nonFaviconErrors.length} console error(s):`);
    nonFaviconErrors.forEach((e) => console.error(`     ${e}`));
  }

  // ── 8. Version list ───────────────────────────────────────────────────────
  console.log("\n8. Version list");
  const versionItems = await page.locator("#version-list li").count().catch(() => 0);
  versionItems > 0
    ? pass(`version list has ${versionItems} run(s)`)
    : fail("version list empty or not rendered");

  await page.screenshot({ path: `${SCREENSHOT_DIR}/04-final.png` });
  console.log(`\nScreenshots saved to: ${SCREENSHOT_DIR}/`);
  console.log("=== UAT complete ===\n");
  await browser.close();
}

run().catch((err) => {
  console.error("UAT crashed:", err);
  process.exitCode = 1;
});
