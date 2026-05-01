// F50 — Version navigator sidebar.
//
// Fetches /api/versions, renders a list in #version-nav, and calls
// onSwitch(sha) when the user selects a different run.

/**
 * Initialize the version navigator.
 *
 * @param {Object} args
 * @param {(sha: string) => void} args.onSwitch  — called when user picks a run
 * @returns {Promise<void>}
 */
export async function initVersionNav({ onSwitch }) {
  const list = document.getElementById("version-list");
  if (!list) return;

  let versions = [];
  try {
    const res = await fetch("/api/versions");
    versions = res.ok ? await res.json() : [];
  } catch {
    versions = [];
  }

  if (versions.length === 0) {
    _renderEmpty(list);
    return;
  }

  // Active SHA comes from the current page URL (last path segment).
  const activeSha = _detectCurrentSha();
  _renderList(list, versions, activeSha, onSwitch);
}

// ---------------------------------------------------------------------------
// Rendering helpers
// ---------------------------------------------------------------------------

function _renderEmpty(list) {
  const li = document.createElement("li");
  li.textContent = "No runs found";
  li.className = "version-empty";
  list.appendChild(li);
}

function _renderList(list, versions, activeSha, onSwitch) {
  list.innerHTML = "";
  versions.forEach((v) => {
    const li = _makeVersionItem(v, activeSha, onSwitch);
    list.appendChild(li);
  });
}

function _makeVersionItem(version, activeSha, onSwitch) {
  const li = document.createElement("li");
  const btn = document.createElement("button");
  btn.type = "button";
  btn.setAttribute("aria-label", `Switch to run ${version.sha} (${version.label})`);
  btn.textContent = `${version.sha.slice(0, 8)} — ${version.label}`;

  if (version.sha === activeSha) {
    btn.classList.add("version-active");
    btn.setAttribute("aria-current", "true");
  }

  btn.addEventListener("click", () => {
    _markActive(li.closest("ul"), btn);
    onSwitch(version.sha);
  });

  li.appendChild(btn);
  return li;
}

function _markActive(list, activeBtn) {
  if (!list) return;
  list.querySelectorAll("button").forEach((b) => {
    b.classList.remove("version-active");
    b.removeAttribute("aria-current");
  });
  activeBtn.classList.add("version-active");
  activeBtn.setAttribute("aria-current", "true");
}

function _detectCurrentSha() {
  // The player is served from drafts/<sha>/index.html.
  // In dev, the URL is just http://localhost:8000/ so we can't reliably
  // detect the SHA from the URL. Return empty string; caller will skip
  // the active highlight.
  return "";
}
