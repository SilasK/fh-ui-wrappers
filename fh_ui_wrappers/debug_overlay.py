"""In-page debug / issue reporter.

A small "BUG" tab sits on the right edge of the page. Clicking it opens a panel
where the user describes a problem; submitting captures a screenshot, the DOM,
the browser console log and (optionally) the last N minutes of the server log
into a folder.

This is the client + bundle-writing half extracted from PartageRivieraDB. The
HTTP endpoints are intentionally not included: they are a few lines and depend
on how your app authenticates. See ``examples/debug_routes.py`` for a FastHTML
adapter using :func:`create_issue_bundle`.

Add :data:`DEBUG_OVERLAY_STYLE` and :func:`debug_overlay_script` to your page
headers, then serve ``GET /debug/overlay/config`` returning
``{"enabled": true|false}`` and ``POST /debug/issue`` accepting the multipart
form built by the script.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from fasthtml.common import Script, Style

_LOG_TS_FORMATS = ("%Y-%m-%d %H:%M:%S,%f", "%Y-%m-%d %H:%M:%S")


def debug_overlay_enabled() -> bool:
    """Global kill switch (default on). ``DEBUG_OVERLAY=0`` disables it."""
    return os.getenv("DEBUG_OVERLAY", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )


def debug_overlay_public() -> bool:
    """Offer the overlay to every visitor, not just admins (dev only).

    Enabled by ``DEBUG_OVERLAY=all`` (also accepts ``public`` / ``everyone``).
    """
    return os.getenv("DEBUG_OVERLAY", "").strip().lower() in (
        "all",
        "public",
        "everyone",
    )


def _parse_log_timestamp(line: str):
    for fmt in _LOG_TS_FORMATS:
        try:
            return datetime.strptime(line[:23] if fmt.endswith("%f") else line[:19], fmt)
        except ValueError:
            continue
    return None


def _recent_log_tail(log_path: Path, minutes: int) -> str:
    """Return lines from the last ``minutes`` minutes of one log file.

    Lines without their own timestamp (tracebacks, continuation lines) are kept
    when the timestamped line they follow was kept, so multi-line errors stay
    readable.
    """
    path = Path(log_path)
    if not path.exists():
        return ""
    cutoff = datetime.now() - timedelta(minutes=minutes)
    kept: list[str] = []
    keep_current = False
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                line = raw.rstrip("\n")
                ts = _parse_log_timestamp(line)
                if ts is not None:
                    keep_current = ts >= cutoff
                if keep_current:
                    kept.append(line)
    except OSError:
        return ""
    return "\n".join(kept)


def recent_server_log(log_dir: str | os.PathLike, minutes: int = 15) -> str:
    """Return ``app.log`` lines from the last ``minutes`` minutes."""
    return _recent_log_tail(Path(log_dir) / "app.log", minutes)


def _slugify(text: str, max_len: int = 40) -> str:
    ascii_text = (
        text.encode("ascii", "ignore").decode("ascii", "ignore").strip().lower()
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return (slug[:max_len].strip("-")) or "issue"


def create_issue_bundle(
    *,
    issue: str,
    url: str,
    dom: str,
    console_log: str,
    admin: str,
    user_agent: str,
    log_dir: str | os.PathLike,
    screenshot: bytes | None = None,
    base_dir: Path | None = None,
    layout_only: bool = False,
    screen_size: dict | None = None,
) -> dict:
    """Write one issue bundle and return ``{"id", "path"}``.

    The description becomes ``issue.md`` with YAML front matter holding the
    machine-readable metadata. ``layout_only`` reduces the bundle to
    ``issue.md`` + ``dom.html`` + ``screenshot.png``.
    """
    base = Path(base_dir) if base_dir else Path("debug/issues")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    folder = base / f"{stamp}-{_slugify(issue)}"
    suffix = 1
    while folder.exists():
        folder = base / f"{stamp}-{_slugify(issue)}-{suffix}"
        suffix += 1
    folder.mkdir(parents=True, exist_ok=True)

    meta = {
        "layout_only": bool(layout_only),
        "url": url,
        "screen": screen_size or {},
        "date": datetime.now().isoformat(timespec="seconds"),
        "admin": admin or "unknown",
        "user_agent": user_agent,
    }
    front_matter = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    (folder / "issue.md").write_text(
        f"---\n{front_matter}\n---\n\nProblème:\n{issue}\n",
        encoding="utf-8",
    )
    (folder / "dom.html").write_text(dom or "", encoding="utf-8")
    if screenshot:
        (folder / "screenshot.png").write_bytes(screenshot)

    if not layout_only:
        (folder / "console.log").write_text(console_log or "", encoding="utf-8")
        (folder / "server.log").write_text(recent_server_log(log_dir), encoding="utf-8")

    return {"id": folder.name, "path": str(folder)}


DEBUG_OVERLAY_STYLE = Style(
    """
#debug-overlay-tab{position:fixed;top:50%;right:0;transform:translateY(-50%);
  z-index:99998;background:#1f2937;color:#fff;border:0;border-radius:6px 0 0 6px;
  padding:10px 5px;cursor:pointer;writing-mode:vertical-rl;font-size:12px;
  letter-spacing:1px;opacity:.75;font-family:system-ui,sans-serif}
#debug-overlay-tab:hover{opacity:1}
#debug-overlay-panel{position:fixed;top:0;right:0;height:100vh;width:360px;
  max-width:92vw;z-index:99999;background:#fff;color:#111;
  box-shadow:-4px 0 16px rgba(0,0,0,.25);display:none;flex-direction:column;
  font-family:system-ui,sans-serif;font-size:13px}
#debug-overlay-panel.open{display:flex}
#debug-overlay-panel .dbo-head{display:flex;align-items:center;
  justify-content:space-between;padding:10px 12px;background:#1f2937;color:#fff}
#debug-overlay-panel .dbo-body{padding:12px;display:flex;flex-direction:column;
  gap:10px;overflow:auto}
#debug-overlay-panel textarea{width:100%;min-height:140px;resize:vertical;
  padding:8px;border:1px solid #cbd5e1;border-radius:6px;font:inherit;
  box-sizing:border-box}
#debug-overlay-panel .dbo-check{display:flex;align-items:center;gap:6px;
  color:#334155;cursor:pointer;user-select:none}
#debug-overlay-panel .dbo-check input{width:auto;margin:0}
#debug-overlay-panel button.dbo-primary{background:#2563eb;color:#fff;border:0;
  border-radius:6px;padding:9px 12px;cursor:pointer;font:inherit}
#debug-overlay-panel button.dbo-primary:disabled{opacity:.6;cursor:default}
#debug-overlay-panel button.dbo-close{background:transparent;border:0;color:#fff;
  font-size:18px;cursor:pointer;line-height:1}
#debug-overlay-status{color:#475569;min-height:16px;word-break:break-word}
#debug-overlay-panel .dbo-note{color:#64748b;font-size:11px}
"""
)


_DEBUG_OVERLAY_JS = r"""
(function(){
  if (window.__dbo) return;
  var D = window.__dbo = {logs: [], enabled: null};

  // Buffer console output + uncaught errors from the very first script run.
  ['log','info','warn','error','debug'].forEach(function(level){
    var orig = console[level];
    console[level] = function(){
      try{
        var parts = Array.prototype.slice.call(arguments).map(function(a){
          if (typeof a === 'string') return a;
          try { return JSON.stringify(a); } catch(e){ return String(a); }
        });
        D.logs.push(new Date().toISOString() + ' [' + level + '] ' + parts.join(' '));
      }catch(e){}
      return orig.apply(console, arguments);
    };
  });
  window.addEventListener('error', function(e){
    D.logs.push(new Date().toISOString() + ' [error] ' + e.message +
                ' @ ' + e.filename + ':' + e.lineno + ':' + e.colno);
  });
  window.addEventListener('unhandledrejection', function(e){
    var r = e.reason;
    D.logs.push(new Date().toISOString() + ' [unhandledrejection] ' +
                ((r && (r.stack || r.message)) || r));
  });

  function loadScript(src){
    return new Promise(function(resolve, reject){
      var s = document.createElement('script');
      s.src = src; s.onload = resolve; s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function captureScreenshot(panel, tab){
    var prevPanel = panel.style.display, prevTab = tab.style.display;
    panel.style.display = 'none'; tab.style.display = 'none';
    var restore = function(){ panel.style.display = prevPanel; tab.style.display = prevTab; };
    var chain = window.html2canvas
      ? Promise.resolve()
      : loadScript('https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js');
    return chain
      .then(function(){ return window.html2canvas(document.body, {useCORS:true, logging:false}); })
      .then(function(canvas){
        return new Promise(function(resolve){
          canvas.toBlob(function(blob){ resolve(blob); }, 'image/png');
        });
      })
      .then(function(blob){ restore(); return blob; })
      .catch(function(err){ restore(); D.logs.push('[debug-overlay] screenshot failed: ' + err); return null; });
  }

  function build(){
    var tab = document.createElement('button');
    tab.id = 'debug-overlay-tab';
    tab.type = 'button';
    tab.textContent = 'BUG';
    tab.title = 'Signaler un problème';

    var panel = document.createElement('div');
    panel.id = 'debug-overlay-panel';
    panel.innerHTML =
      '<div class="dbo-head"><strong>Signaler un problème</strong>' +
      '<button type="button" class="dbo-close" aria-label="Fermer">&times;</button></div>' +
      '<div class="dbo-body">' +
      '<textarea id="debug-overlay-text" placeholder="Décrivez le problème…"></textarea>' +
      '<label class="dbo-check"><input type="checkbox" id="debug-overlay-layout"> Layout only</label>' +
      '<button type="button" class="dbo-primary" id="debug-overlay-send">Capturer et envoyer</button>' +
      '<div id="debug-overlay-status"></div>' +
      '<div class="dbo-note">Envoie: capture d\'écran, DOM, console JS et le journal serveur récent.</div>' +
      '</div>';

    document.body.appendChild(tab);
    document.body.appendChild(panel);

    var textarea = panel.querySelector('#debug-overlay-text');
    var layout = panel.querySelector('#debug-overlay-layout');
    var sendBtn = panel.querySelector('#debug-overlay-send');
    var status = panel.querySelector('#debug-overlay-status');
    var closeBtn = panel.querySelector('.dbo-close');

    tab.addEventListener('click', function(){ panel.classList.toggle('open'); });
    closeBtn.addEventListener('click', function(){ panel.classList.remove('open'); });

    sendBtn.addEventListener('click', function(){
      var issue = (textarea.value || '').trim();
      if (!issue){ status.textContent = 'Décrivez le problème avant d\'envoyer.'; return; }
      sendBtn.disabled = true;
      status.textContent = 'Capture en cours…';
      captureScreenshot(panel, tab).then(function(blob){
        var fd = new FormData();
        fd.append('issue', issue);
        fd.append('url', location.href);
        fd.append('layout_only', layout.checked ? 'true' : 'false');
        fd.append('screen_size', JSON.stringify({
            w: window.innerWidth,
            h: window.innerHeight,
            dpr: window.devicePixelRatio || 1
        }));
        fd.append('dom', document.documentElement.outerHTML);
        fd.append('console_log', D.logs.join('\n'));
        if (blob) fd.append('screenshot', blob, 'screenshot.png');
        status.textContent = 'Envoi…';
        var csrf = (window.__csrf && window.__csrf.token) || '';
        return fetch(__ISSUE_URL__, {method:'POST', body: fd,
          headers: csrf ? {'X-CSRF-Token': csrf} : {}});
      }).then(function(resp){
        return resp.json().then(function(data){ return {ok: resp.ok, data: data}; });
      }).then(function(res){
        if (res.ok && res.data.ok){
          status.textContent = 'Envoyé: ' + res.data.id;
          textarea.value = '';
        } else {
          status.textContent = 'Erreur: ' + ((res.data && res.data.error) || 'inconnue');
        }
        sendBtn.disabled = false;
      }).catch(function(err){
        status.textContent = 'Erreur réseau: ' + err;
        sendBtn.disabled = false;
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    fetch(__CONFIG_URL__, {headers: {'Accept': 'application/json'}})
      .then(function(r){ return r.json(); })
      .then(function(cfg){ if (cfg && cfg.enabled) build(); })
      .catch(function(){});
  });
})();
"""


def debug_overlay_script(
    config_url: str = "/debug/overlay/config",
    issue_url: str = "/debug/issue",
):
    """Return the client ``Script`` with configurable endpoint URLs."""
    js = _DEBUG_OVERLAY_JS.replace(
        "__CONFIG_URL__", json.dumps(config_url)
    ).replace("__ISSUE_URL__", json.dumps(issue_url))
    return Script(js)


def debug_overlay_headers(
    config_url: str = "/debug/overlay/config",
    issue_url: str = "/debug/issue",
):
    """Return ``(style, script)`` for ``fast_app(hdrs=...)``."""
    return DEBUG_OVERLAY_STYLE, debug_overlay_script(config_url, issue_url)


__all__ = [
    "DEBUG_OVERLAY_STYLE",
    "create_issue_bundle",
    "debug_overlay_enabled",
    "debug_overlay_headers",
    "debug_overlay_public",
    "debug_overlay_script",
    "recent_server_log",
]
