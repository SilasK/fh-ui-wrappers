"""Overlay helpers: zoomable photo viewer and modal boilerplate.

Extracted from PartageRivieraDB's ``utils/ui_components.py`` (photo overlay)
and its MonsterUI modal usage.

Include :func:`photo_overlay_script` once per page (it is declared as a
FastHTML ``Script`` you can drop into ``fast_app(hdrs=...)``), then call
:func:`photo_thumb` for any image that should open full-screen on click.
"""

from __future__ import annotations

from fasthtml.common import Img, Script, unqid
from monsterui.all import Modal as _Modal
from monsterui.all import ModalCloseButton, ModalTitle

from .buttons import Button

PHOTO_OVERLAY_SCRIPT = Script(
    r"""
function openPhotoOverlay(src){
    const existing = document.getElementById('photo-overlay');
    if(existing) existing.remove();
    const overlay = document.createElement('div');
    overlay.id = 'photo-overlay';
    overlay.style.cssText = 'position:fixed;left:0;top:0;width:100vw;height:100vh;background:rgba(0,0,0,0.85);z-index:9999;display:flex;align-items:center;justify-content:center;';
    const img = document.createElement('img');
    img.src = src;
    img.style.cssText = 'max-width:95%;max-height:95%;cursor:zoom-in;transition:transform .15s ease;';
    let scale = 1;
    function close(){ overlay.remove(); document.removeEventListener('keydown', onKey); }
    function onKey(e){ if(e.key === 'Escape') close(); }
    overlay.addEventListener('wheel', function(e){
        e.preventDefault();
        scale += -(e.deltaY || e.wheelDelta) > 0 ? 0.1 : -0.1;
        scale = Math.max(0.5, Math.min(5, scale));
        img.style.transform = 'scale(' + scale + ')';
        img.style.cursor = scale > 1 ? 'zoom-out' : 'zoom-in';
    });
    overlay.addEventListener('click', function(e){
        if(e.target === overlay) close();
    });
    document.addEventListener('keydown', onKey);
    overlay.appendChild(img);
    document.body.appendChild(overlay);
}
"""
)


def photo_overlay_script():
    """Return the ``openPhotoOverlay(src)`` script for page headers."""
    return PHOTO_OVERLAY_SCRIPT


def photo_thumb(
    src,
    *,
    alt="",
    cls="w-32 h-32 object-cover rounded-lg shadow-sm cursor-pointer",
    **kwargs,
):
    """An image that opens the zoomable overlay when clicked.

    Example:
        >>> photo_thumb("/photos/portrait.jpg", alt="Portrait")
    """
    kwargs.setdefault("onclick", "openPhotoOverlay(this.src)")
    return Img(src=src, alt=alt, cls=cls, **kwargs)


def Modal(
    *body,
    title=None,
    footer=None,
    modal_id=None,
    dialog_cls="max-w-lg",
    **kwargs,
):
    """MonsterUI modal with fewer required arguments.

    Args:
        body: modal body contents.
        title: optional title rendered in the header.
        footer: optional footer contents.
        modal_id: DOM id (generated when omitted).
        dialog_cls: classes on the dialog (default ``max-w-lg``).
        **kwargs: forwarded to MonsterUI's ``Modal`` (``hx_open``, ...).

    Example:
        >>> Modal(Form(...), title="Planifier", modal_id="plan-modal",
        ...       footer=ModalCloseButton("Annuler"))
    """
    return _Modal(
        *body,
        header=ModalTitle(title) if title else None,
        footer=footer,
        id=modal_id or unqid(),
        dialog_cls=dialog_cls,
        **kwargs,
    )


def ModalTrigger(
    *children,
    target,
    icon=None,
    variant="default",
    **kwargs,
):
    """A button that opens a modal by id (``uk-toggle``).

    Example:
        >>> ModalTrigger("Planifier maintenant", target="plan-modal",
        ...              icon="calendar")
    """
    kwargs.setdefault("uk-toggle", f"target: #{target}")
    return Button(*children, icon=icon, variant=variant, **kwargs)


__all__ = [
    "PHOTO_OVERLAY_SCRIPT",
    "Modal",
    "ModalCloseButton",
    "ModalTitle",
    "ModalTrigger",
    "photo_overlay_script",
    "photo_thumb",
]
