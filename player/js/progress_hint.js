// F39 DE-04 — ProgressHint element ("שאלה N מתוך M").
//
// Pure DOM element + render. No state, no fetch. The render function
// returned by `mountProgressHint` is bound to the created element.

export function mountProgressHint(parent) {
  const el = document.createElement("span");
  el.className = "progress-hint";
  el.setAttribute("aria-live", "polite");
  parent.appendChild(el);
  const render = (state) => renderProgressHint(el, state);
  return { el, render };
}

export function renderProgressHint(el, { current, total }) {
  if (total <= 0) {
    el.hidden = true;
    el.textContent = "";
    return;
  }
  el.hidden = false;
  el.textContent = `שאלה ${current} מתוך ${total}`;
}
