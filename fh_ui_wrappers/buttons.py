"""Button helpers.

Extracted from PartageRivieraDB, where every button was written by hand as
``Button(..., cls="uk-btn uk-btn-primary")``. These helpers centralise the
variant names and the "icon + label" pattern.

The module deliberately shadows MonsterUI's ``Button``: import it instead of
MonsterUI's when you want the variant API.
"""

from __future__ import annotations

from fasthtml.common import A, Button as _Button, Span
from monsterui.all import UkIcon

#: Franken UI button variants used across the app.
BUTTON_VARIANTS = {
    "primary": "uk-btn-primary",
    "secondary": "uk-btn-secondary",
    "danger": "uk-btn-danger",
    "destructive": "uk-btn-destructive",
    "ghost": "uk-btn-ghost",
    "default": "uk-btn-default",
    "text": "uk-btn-text",
    "link": "uk-btn-link",
    "icon": "uk-btn-icon",
}

#: Optional size modifiers.
BUTTON_SIZES = {
    "xs": "uk-btn-xs",
    "sm": "uk-btn-sm",
    "lg": "uk-btn-lg",
    "xl": "uk-btn-xl",
}


def _icon(name, cls=""):
    """An icon with classes only when there are any (keeps HTML clean)."""
    return UkIcon(name, cls=cls) if cls else UkIcon(name)


def _classes(variant=None, size=None, cls="", extra=()):
    """Build a de-duplicated class string in a stable order."""
    classes = ["uk-btn"]
    if variant:
        classes.append(BUTTON_VARIANTS.get(variant, variant))
    if size:
        classes.append(BUTTON_SIZES.get(size, size))
    classes.extend(extra)
    if cls:
        if isinstance(cls, (list, tuple)):
            classes.extend(cls)
        else:
            classes.append(cls)
    return " ".join(dict.fromkeys(c for c in classes if c))


def Button(
    *children,
    variant="primary",
    size=None,
    icon=None,
    icon_cls="mr-1",
    cls="",
    submit=False,
    **kwargs,
):
    """A styled ``<button>``.

    Args:
        children: button contents (usually a label).
        variant: key from :data:`BUTTON_VARIANTS` or a raw ``uk-btn-*`` class.
        size: ``xs`` / ``sm`` / ``lg`` / ``xl``.
        icon: optional icon name rendered before the label (e.g. ``"plus"``).
        icon_cls: classes on the icon.
        cls: extra classes.
        submit: when True the button submits its form (``type="submit"``);
            the default is ``type="button"`` so action buttons never submit
            a surrounding form by accident.
        **kwargs: any other HTML attribute (``onclick``, ``hx_post``, ...).

    Example:
        >>> Button("Enregistrer", submit=True)
        >>> Button("Supprimer", variant="danger", hx_post="/delete")
        >>> Button("Planifier", icon="calendar", **{"uk-toggle": "target: #plan-modal"})
    """
    if "type" not in kwargs:
        kwargs["type"] = "submit" if submit else "button"
    content = [_icon(icon, icon_cls)] if icon else []
    content.extend(children)
    return _Button(*content, cls=_classes(variant, size, cls), **kwargs)


def IconButton(
    icon,
    *,
    text=None,
    label=None,
    variant="ghost",
    size=None,
    cls="",
    icon_cls="",
    **kwargs,
):
    """An icon-only button with an accessible name.

    ``label`` is used for ``aria-label``/``title`` when there is no visible
    text. Pass ``text`` for an icon + visible label.

    Example:
        >>> IconButton("camera", label="Prendre une photo", onclick="openCamera()")
        >>> IconButton("trash", label="Supprimer", variant="danger")
        >>> IconButton("plus", text="Ajouter", variant="primary", size="sm")
    """
    accessible_name = label or (text if isinstance(text, str) else None)
    if accessible_name:
        kwargs.setdefault("aria-label", accessible_name)
        kwargs.setdefault("title", accessible_name)
    if text is not None and not icon_cls:
        icon_cls = "mr-1"
    content = [_icon(icon, icon_cls)] if icon else []
    if text is not None:
        content.append(Span(text))
    return Button(
        *content,
        variant=variant,
        size=size,
        cls=cls,
        **kwargs,
    )


def LinkButton(
    *children,
    href,
    variant="primary",
    size=None,
    icon=None,
    icon_cls="mr-1",
    cls="",
    **kwargs,
):
    """A link styled like a button (``<a class="uk-btn ...">``).

    Example:
        >>> LinkButton("Retour", href="/admin", icon="arrow-left", variant="ghost")
    """
    content = [_icon(icon, icon_cls)] if icon else []
    content.extend(children)
    return A(*content, href=href, cls=_classes(variant, size, cls), **kwargs)


def NavLink(label, href, *, active=False, icon=None, cls="", **kwargs):
    """Navbar link with an optional icon and an active state.

    Extracted from ``utils/layout.py::_nav_link``.

    Example:
        >>> NavLink("Tableau de bord", "/admin", active=True, icon="home")
    """
    classes = "uk-btn uk-btn-ghost text-sm inline-flex items-center"
    if active:
        classes += " font-semibold text-primary"
    if cls:
        classes += f" {cls}"
    content = [UkIcon(icon, cls="mr-1")] if icon else []
    content.append(Span(label))
    return A(*content, href=href, cls=classes, **kwargs)
