// F39 T-05 — ProgressHint element ("שאלה N מתוך M").
//
// Spec: N04/F39 DE-04. AC: F39-S05/AC-01.
// Covers FT-272 (text format), FT-274 (hidden when 0 questions).

import { describe, it, expect, beforeEach } from "vitest";
import {
  mountProgressHint,
  renderProgressHint,
} from "../js/progress_hint.js";

describe("F39 T-05 — mountProgressHint", () => {
  let parent;

  beforeEach(() => {
    parent = document.createElement("div");
  });

  it("appends a <span> to parent and returns {el, render}", () => {
    const result = mountProgressHint(parent);
    expect(result.el).toBeInstanceOf(HTMLSpanElement);
    expect(result.el.parentElement).toBe(parent);
    expect(typeof result.render).toBe("function");
  });

  it("the span has aria-live=\"polite\" and class \"progress-hint\"", () => {
    const { el } = mountProgressHint(parent);
    expect(el.getAttribute("aria-live")).toBe("polite");
    expect(el.classList.contains("progress-hint")).toBe(true);
  });

  it("ft_272 — render({current:1, total:3}) sets textContent to \"שאלה 1 מתוך 3\"", () => {
    const { el, render } = mountProgressHint(parent);
    render({ current: 1, total: 3 });
    expect(el.textContent).toBe("שאלה 1 מתוך 3");
  });

  it("re-render updates textContent — {current:2, total:3} → \"שאלה 2 מתוך 3\"", () => {
    const { el, render } = mountProgressHint(parent);
    render({ current: 1, total: 3 });
    render({ current: 2, total: 3 });
    expect(el.textContent).toBe("שאלה 2 מתוך 3");
  });

  it("render({current:1, total:1}) → \"שאלה 1 מתוך 1\"", () => {
    const { el, render } = mountProgressHint(parent);
    render({ current: 1, total: 1 });
    expect(el.textContent).toBe("שאלה 1 מתוך 1");
  });

  it("ft_274 — render({current:0, total:0}) sets el.hidden = true", () => {
    const { el, render } = mountProgressHint(parent);
    render({ current: 0, total: 0 });
    expect(el.hidden).toBe(true);
  });

  it("after hidden, render({current:1, total:2}) sets el.hidden = false again", () => {
    const { el, render } = mountProgressHint(parent);
    render({ current: 0, total: 0 });
    expect(el.hidden).toBe(true);
    render({ current: 1, total: 2 });
    expect(el.hidden).toBe(false);
    expect(el.textContent).toBe("שאלה 1 מתוך 2");
  });

  it("the bound render updates the same el across calls", () => {
    const { el, render } = mountProgressHint(parent);
    render({ current: 1, total: 4 });
    const elAfterFirst = parent.querySelector(".progress-hint");
    render({ current: 3, total: 4 });
    const elAfterSecond = parent.querySelector(".progress-hint");
    expect(elAfterFirst).toBe(el);
    expect(elAfterSecond).toBe(el);
    expect(parent.querySelectorAll(".progress-hint").length).toBe(1);
  });
});

describe("F39 T-05 — renderProgressHint (pure)", () => {
  it("updates an existing span's textContent and hidden", () => {
    const span = document.createElement("span");
    renderProgressHint(span, { current: 2, total: 5 });
    expect(span.textContent).toBe("שאלה 2 מתוך 5");
    expect(span.hidden).toBe(false);
  });

  it("hides the element when total is 0", () => {
    const span = document.createElement("span");
    renderProgressHint(span, { current: 0, total: 0 });
    expect(span.hidden).toBe(true);
  });
});
