"""Form control helpers: plain labels, dropdowns and checkboxes.

The patterns come from PartageRivieraDB:

* MonsterUI's ``Label`` renders a ``uk-label`` badge, which turns ordinary form
  labels into coloured pills. :func:`Label` renders a plain ``<label>``.
* MonsterUI's ``Select`` bridges the ``<uk-select>`` custom element. A literal
  ``hx-trigger`` attribute bypasses that bridge (the event never fires), so
  :func:`Dropdown` translates ``hx-trigger`` into the underscore form the
  bridge understands.
* Checkbox rows in the planning modal pair a styled checkbox with a title and
  a muted description line; :func:`CheckboxRow` packages that layout.
"""

from __future__ import annotations

from collections.abc import Mapping

from fasthtml.common import (
    Div,
    Hidden,
    Label as _Label,
    Option,
    Select as _NativeSelect,
    Span,
)
from monsterui.all import CheckboxX as _CheckboxX
from monsterui.all import LabelSelect as _MLabelSelect
from monsterui.all import Select as _MSelect


def Label(*c, cls="", **kwargs):
    """A plain ``<label>`` without MonsterUI's ``uk-label`` pill styling."""
    if cls:
        kwargs["cls"] = cls
    return _Label(*c, **kwargs)


def _option_pairs(options, value_attr, label_attr):
    """Normalise dict / tuple / string / object options into (value, label)."""
    if isinstance(options, Mapping):
        return list(options.items())
    pairs = []
    for item in options:
        if isinstance(item, str):
            pairs.append((item, item))
        elif isinstance(item, Mapping):
            pairs.append((item[value_attr], item[label_attr]))
        elif isinstance(item, (tuple, list)) and len(item) >= 2:
            pairs.append((item[0], item[1]))
        else:
            pairs.append((getattr(item, value_attr), getattr(item, label_attr)))
    return pairs


def _selected_values(value, multiple):
    if value is None:
        return set()
    if multiple or isinstance(value, (list, tuple, set)):
        return {str(v) for v in value}
    return {str(value)}


def Dropdown(
    options=(),
    *,
    name=None,
    value=None,
    label=None,
    placeholder=None,
    cls="uk-select",
    native=False,
    multiple=False,
    value_attr="value",
    label_attr="label",
    container_cls=None,
    component_cls="",
    label_cls="",
    **kwargs,
):
    """A styled ``<select>`` dropdown, optionally with a label.

    With ``label=...`` this returns MonsterUI's ``LabelSelect`` (a
    ``FormLabel`` + ``Select`` pair, so the label is a proper ``uk-form-label``,
    not the pill-shaped ``uk-label``). Without a label it returns the bare
    ``Select``.

    Args:
        options: any of ``{value: label}``, ``[(value, label), ...]``, a list of
            strings, or objects with ``value_attr`` / ``label_attr`` attributes.
        name: form field name.
        value: selected value (or iterable of values when ``multiple=True``).
        label: optional visible label. When given, uses ``LabelSelect`` and the
            ``id`` defaults to ``name`` so label and control are linked.
        placeholder: optional first option shown when nothing is selected.
        cls: classes on the native ``<select>`` (default keeps the UK styling).
        native: return a plain ``<select>`` instead of MonsterUI's JS bridge.
            Use this when the form must submit the chosen value reliably.
        multiple: allow multiple selection. This always uses the native
            ``<select>`` because MonsterUI's bridge does not forward
            ``multiple`` to the inner control.
        value_attr / label_attr: attribute names used when ``options`` contains
            objects (e.g. ``value_attr="group_id", label_attr="name"``).
        container_cls: classes on the outer wrapper ``<div>``. Defaults to
            ``"space-y-2 w-full"`` when labelled and ``"w-full"`` otherwise.
        component_cls: classes on the ``<uk-select>`` custom element.
        label_cls: extra classes on the ``FormLabel`` (or plain label when
            ``native=True``).

    Example:
        >>> Dropdown({"a": "Groupe A", "b": "Groupe B"}, name="group", value="a",
        ...          label="Groupe")
        >>> Dropdown(groups, name="group_id", label="Groupe",
        ...          value_attr="group_id", label_attr="name",
        ...          placeholder="Choisir…")
        >>> Dropdown(options, name="date", label="Date", native=True,
        ...          cls="uk-select w-44")
    """
    # MonsterUI's bridge only rewrites the underscore kwarg.
    if "hx-trigger" in kwargs:
        kwargs["hx_trigger"] = kwargs.pop("hx-trigger")

    select_id = kwargs.pop("id", None)
    selected = _selected_values(value, multiple)
    opts = []
    if placeholder is not None:
        opts.append(
            Option(
                placeholder,
                value="",
                disabled=True,
                selected=(not selected),
            )
        )
    for opt_value, opt_label in _option_pairs(options, value_attr, label_attr):
        opts.append(
            Option(
                opt_label,
                value=str(opt_value),
                selected=(str(opt_value) in selected),
            )
        )

    resolved_container = (
        container_cls
        if container_cls is not None
        else ("space-y-2 w-full" if label is not None else "w-full")
    )

    # MonsterUI's bridge does not forward ``multiple`` to the inner native
    # control, so a multi-select always uses the native element.
    if native or multiple:
        native_id = select_id or (name if label is not None else None)
        select_el = _NativeSelect(
            *opts,
            name=name,
            id=native_id,
            multiple=multiple or None,
            cls=cls,
            **kwargs,
        )
        if label is None:
            return select_el
        label_attrs = {"for": native_id} if native_id else {}
        return Div(
            Label(label, cls=label_cls, **label_attrs),
            select_el,
            cls=resolved_container,
        )

    if label is not None:
        select_kwargs = {"cls": cls} if cls else None
        return _MLabelSelect(
            *opts,
            label=label,
            lbl_cls=label_cls,
            name=name or "",
            id=select_id or (name or ""),
            inp_cls=component_cls,
            cls=resolved_container,
            select_kwargs=select_kwargs,
            **kwargs,
        )

    select_kwargs = {"cls": cls} if cls else None
    return _MSelect(
        *opts,
        name=name or "",
        id=select_id or "",
        inp_cls=component_cls,
        cls=resolved_container,
        select_kwargs=select_kwargs,
        **kwargs,
    )


def Checkbox(
    *,
    name=None,
    value="1",
    checked=False,
    label=None,
    disabled=False,
    cls="",
    label_cls=None,
    include_hidden=False,
    **kwargs,
):
    """A styled checkbox, optionally wrapped in a label.

    Args:
        name: form field name.
        value: value submitted when checked.
        checked: initial state.
        label: when given, wraps the input in a clickable ``<label>``.
        disabled: disable the control.
        cls: extra classes on the ``<input>``.
        label_cls: classes on the wrapping label (sensible default provided).
        include_hidden: emit a hidden empty field first, so an unchecked box
            still submits ``name=""`` (useful for single boolean fields; do
            not use it for repeated ``name`` values).

    Example:
        >>> Checkbox(name="paid", label="Payé", checked=True)
    """
    box = _CheckboxX(
        name=name,
        value=value,
        checked=True if checked else None,
        disabled=True if disabled else None,
        cls=cls,
        **kwargs,
    )
    if include_hidden:
        box = (Hidden(name=name, value=""), box)
    if label is None:
        return box
    return Label(
        box,
        label,
        cls=label_cls or "flex items-center gap-2 cursor-pointer",
    )


def CheckboxRow(
    name,
    value,
    label,
    *,
    description=None,
    checked=False,
    disabled=False,
    extra=None,
    cls="",
    label_cls=None,
    **kwargs,
):
    """Checkbox row with a bold title, muted description and optional right slot.

    Mirrors the group-selection rows in the "Planifier maintenant" modal.

    Example:
        >>> CheckboxRow(
        ...     "group_ids", group.group_id, group.name,
        ...     description=f"— {headcount} bénéficiaires",
        ...     checked=eligible,
        ...     disabled=not eligible,
        ...     extra=date_select,
        ... )
    """
    text = Div(
        Span(label, cls="font-medium"),
        Span(description, cls="text-sm text-gray-500") if description else None,
        cls="flex items-center gap-2",
    )
    row = Label(
        _CheckboxX(
            name=name,
            value=value,
            checked=True if checked else None,
            disabled=True if disabled else None,
            cls="mr-2",
            **kwargs,
        ),
        text,
        cls=label_cls
        or ("flex items-center gap-2 cursor-pointer" + ("" if disabled else " hover:bg-gray-50")),
    )
    if extra is None:
        return row
    return Div(row, extra, cls=cls or "flex items-center justify-between gap-3 py-1")
