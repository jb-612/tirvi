// N04/F33 T-07 — preview.js: renderArtifact artifact content renderer.
// DE-03  AC: US-03/AC-12, US-05/AC-23
// FT-319, FT-322  BT-213, BT-217

/**
 * Render an artifact into panel, dispatching by file extension.
 *
 * @param {{ url: string, name: string, stage: string }} artifact
 * @param {HTMLElement} panel - DOM element to render into (cleared first).
 */
export async function renderArtifact({ url, name, stage }, panel) {
  panel.innerHTML = "";

  const ext = _ext(name);

  if (_isImage(ext)) {
    return _renderImage(url, name, panel);
  }
  if (_isAudio(ext)) {
    return _renderAudio(url, panel);
  }
  if (!_isText(ext)) {
    return _renderUnknown(panel);
  }

  let text;
  try {
    const resp = await fetch(url);
    text = await resp.text();
  } catch (_) {
    return _renderFetchError(panel);
  }

  if (ext === ".json") {
    return _renderJson(text, panel);
  }
  return _renderText(text, panel);
}

// ---------------------------------------------------------------------------
// Extension helpers (CC ≤ 5 each)
// ---------------------------------------------------------------------------

function _ext(name) {
  const dot = name.lastIndexOf(".");
  return dot === -1 ? "" : name.slice(dot).toLowerCase();
}

function _isImage(ext) {
  return ext === ".png" || ext === ".jpg" || ext === ".jpeg";
}

function _isAudio(ext) {
  return ext === ".mp3" || ext === ".wav";
}

function _isText(ext) {
  return ext === ".json" || ext === ".txt" || ext === ".ssml";
}

// ---------------------------------------------------------------------------
// Renderers (CC ≤ 5 each)
// ---------------------------------------------------------------------------

function _renderImage(url, name, panel) {
  const img = document.createElement("img");
  img.className = "preview-image";
  img.src = url;
  img.alt = name;
  panel.appendChild(img);
}

function _renderAudio(url, panel) {
  const audio = document.createElement("audio");
  audio.className = "preview-audio";
  audio.controls = true;
  audio.src = url;
  panel.appendChild(audio);
}

function _renderUnknown(panel) {
  const p = document.createElement("p");
  p.className = "preview-unknown";
  p.textContent = "Preview not available for this file type";
  panel.appendChild(p);
}

function _renderFetchError(panel) {
  const p = document.createElement("p");
  p.className = "preview-error";
  p.textContent = "Failed to load artifact";
  panel.appendChild(p);
}

function _renderEmpty(panel) {
  const p = document.createElement("p");
  p.className = "preview-empty";
  p.textContent = "(empty)";
  panel.appendChild(p);
}

function _renderJson(text, panel) {
  let pretty;
  try {
    const parsed = JSON.parse(text);
    if (_isEmptyCollection(parsed)) {
      return _renderEmpty(panel);
    }
    pretty = JSON.stringify(parsed, null, 2);
  } catch (_) {
    pretty = text;
  }

  const pre = document.createElement("pre");
  pre.className = "preview-json";
  const code = document.createElement("code");
  code.textContent = pretty;
  pre.appendChild(code);
  panel.appendChild(pre);
}

function _isEmptyCollection(parsed) {
  if (Array.isArray(parsed)) return parsed.length === 0;
  if (parsed !== null && typeof parsed === "object") {
    return Object.keys(parsed).length === 0;
  }
  return false;
}

function _renderText(text, panel) {
  if (text === "") {
    return _renderEmpty(panel);
  }
  const pre = document.createElement("pre");
  pre.className = "preview-text";
  pre.textContent = text;
  panel.appendChild(pre);
}
