"""Example FastHTML endpoints for the debug overlay.

Wire them into your app after creating ``app, rt = fast_app(...)``::

    from examples.debug_routes import register_debug_overlay
    register_debug_overlay(rt, base_dir=Path("debug/issues"), log_dir=Path("logs"))

Pass ``is_admin`` (a callable taking the session and returning truthy for an
admin) to restrict submissions. Without it every visitor can submit, which is
only appropriate for a dev deployment. ``DEBUG_OVERLAY=all`` opens it to every
visitor even when ``is_admin`` is set.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fasthtml.common import JSONResponse

from fh_ui_wrappers.debug_overlay import (
    create_issue_bundle,
    debug_overlay_enabled,
    debug_overlay_public,
    session_reporter,
)


def register_debug_overlay(
    rt,
    *,
    base_dir: str | Path = "debug/issues",
    log_dir: str | Path = "logs",
    is_admin=None,
):
    """Register ``/debug/overlay/config`` and ``/debug/issue``."""

    def _allowed(session) -> bool:
        if not debug_overlay_enabled():
            return False
        if debug_overlay_public():
            return True
        return bool(is_admin(session)) if is_admin else True

    @rt("/debug/overlay/config", methods=["GET"])
    def debug_overlay_config(session):
        return JSONResponse({"enabled": _allowed(session)})

    @rt("/debug/issue", methods=["POST"])
    async def debug_issue_post(request, session):
        if not _allowed(session):
            return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=403)

        form = await request.form()
        screenshot = form.get("screenshot")
        screenshot_bytes = None
        if screenshot is not None and hasattr(screenshot, "read"):
            screenshot_bytes = await screenshot.read()

        screen_size: dict = {}
        screen_raw = form.get("screen_size")
        if screen_raw:
            try:
                screen_size = json.loads(screen_raw)
            except (json.JSONDecodeError, TypeError):
                screen_size = {}

        try:
            result = create_issue_bundle(
                issue=str(form.get("issue", "")),
                url=str(form.get("url", "")),
                dom=str(form.get("dom", "")),
                console_log=str(form.get("console_log", "")),
                user_agent=request.headers.get("user-agent", ""),
                log_dir=log_dir,
                base_dir=Path(base_dir),
                screenshot=screenshot_bytes,
                layout_only=str(form.get("layout_only", "")).strip().lower()
                in ("1", "true", "on", "yes"),
                screen_size=screen_size,
                reporter=session_reporter(session),
            )
        except Exception as exc:  # never break the reporter itself
            logging.exception("debug issue bundle failed")
            return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)

        return JSONResponse({"ok": True, **result})
