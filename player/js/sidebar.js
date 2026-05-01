// N04/F33 T-06 — sidebar.js: mountArtifactTree
// DE-03  AC: US-03/AC-11, US-03/AC-13, US-03/AC-14
// FT-320, FT-321, FT-325, FT-329  BT-211

/**
 * Render an artifact tree into container from manifest.json at rootUrl.
 *
 * @param {HTMLElement} container - DOM element to render into.
 * @param {string} rootUrl - Base URL for the run; manifest at rootUrl/manifest.json.
 * @param {object} [opts]
 * @param {function} [opts.onArtifactClick] - Called with {url, name, stage} on file click.
 */
export async function mountArtifactTree(container, rootUrl, { onArtifactClick } = {}) {
  container.innerHTML = "";

  let manifest;
  try {
    const resp = await fetch(`${rootUrl}/manifest.json`);
    if (!resp.ok) {
      return _renderError(container);
    }
    manifest = await resp.json();
  } catch (_) {
    return _renderError(container);
  }

  const stages = manifest.stages ?? [];
  if (stages.length === 0) {
    return _renderEmpty(container);
  }

  const ul = _buildTree(stages, rootUrl, onArtifactClick);
  container.appendChild(ul);
}

// ---------------------------------------------------------------------------
// Private helpers (CC ≤ 5 each)
// ---------------------------------------------------------------------------

function _renderError(container) {
  const p = document.createElement("p");
  p.className = "artifact-error";
  p.textContent = "Unable to load artifacts";
  container.appendChild(p);
}

function _renderEmpty(container) {
  const p = document.createElement("p");
  p.className = "artifact-empty";
  p.textContent = "No stages available";
  container.appendChild(p);
}

function _buildTree(stages, rootUrl, onArtifactClick) {
  const ul = document.createElement("ul");
  ul.className = "artifact-tree";
  ul.setAttribute("aria-label", "Artifact stages");
  for (const stage of stages) {
    ul.appendChild(_buildStage(stage, rootUrl, onArtifactClick));
  }
  return ul;
}

function _buildStage(stage, rootUrl, onArtifactClick) {
  const li = document.createElement("li");
  li.className = "artifact-stage";

  const btn = document.createElement("button");
  btn.className = "stage-header";
  btn.textContent = stage.label;
  li.appendChild(btn);

  if (!stage.available) {
    const span = document.createElement("span");
    span.className = "stage-unavailable";
    span.textContent = "Not available";
    li.appendChild(span);
    return li;
  }

  li.appendChild(_buildFileList(stage, rootUrl, onArtifactClick));
  return li;
}

function _buildFileList(stage, rootUrl, onArtifactClick) {
  const ul = document.createElement("ul");
  ul.className = "artifact-files";
  for (const filename of stage.files) {
    ul.appendChild(_buildFileItem(filename, stage, rootUrl, onArtifactClick));
  }
  return ul;
}

function _buildFileItem(filename, stage, rootUrl, onArtifactClick) {
  const li = document.createElement("li");
  const url = `${rootUrl}/${stage.name}/${filename}`;
  const btn = document.createElement("button");
  btn.className = "artifact-file";
  btn.dataset.url = url;
  btn.textContent = filename;
  btn.addEventListener("click", () => {
    if (onArtifactClick) {
      onArtifactClick({ url, name: filename, stage: stage.name });
    }
  });
  li.appendChild(btn);
  return li;
}
