// F35/F36 — Orchestration entry point.
//
// Wires bootPlayer → page image → marker → play button → highlight loop.
// Auto-executes on module load so index.html only needs this one script tag.

import { bootPlayer } from "./player.js";
import { mountPlayButton } from "./controls.js";
import { startHighlightLoop } from "./highlight.js";

export async function init() {
  try {
    const state = await bootPlayer();

    const fig = document.getElementById("page-figure");
    const img = document.createElement("img");
    img.id = "page-image";
    img.src = state.pageProjection.page_image_url;
    img.alt = "";
    fig.appendChild(img);

    const marker = document.createElement("div");
    marker.id = "word-marker";
    marker.className = "marker";
    marker.style.visibility = "hidden";
    fig.appendChild(marker);

    const toolbar = document.getElementById("controls");
    mountPlayButton({ audio: state.audio, toolbar });

    let stopLoop = null;
    state.audio.addEventListener("play", () => {
      stopLoop = startHighlightLoop({
        audio: state.audio,
        marker,
        pageImage: img,
        timings: state.timings,
        pageProjection: state.pageProjection,
      });
    });
    state.audio.addEventListener("pause", () => {
      if (stopLoop) {
        stopLoop();
        stopLoop = null;
      }
    });
  } catch (e) {
    console.error("[tirvi init]", e);
  }
}

init();
