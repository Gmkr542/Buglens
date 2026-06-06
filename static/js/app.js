// app.js — BugLens companion utilities
// NOTE: The main application logic is embedded in templates/index.html.
// This file provides utility helpers that can be imported by other pages.

// ── JSZip CDN (loaded lazily on demand) ──
let JSZip = null;
async function loadJSZip() {
  if (JSZip) return JSZip;
  return new Promise((res, rej) => {
    const s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
    s.onload = () => { JSZip = window.JSZip; res(JSZip); };
    s.onerror = rej;
    document.head.appendChild(s);
  });
}

function formatBytes(b) {
  if (b < 1024) return b + ' B';
  if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1024 / 1024).toFixed(1) + ' MB';
}

function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
