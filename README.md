# fh-ui-wrappers

Reusable [FastHTML](https://www.fastht.ml/) + [MonsterUI](https://monsterui.answer.ai/)
UI wrappers, extracted from the PartageRiviera app and generalised for reuse.

Everything here is intentionally small and copy-paste friendly: one module per
family of controls, no framework, no build step. Edit the files directly — this
is a reference library, not a released package.

## What is in the box

| Module | Helpers |
| --- | --- |
| `buttons.py` | `Button`, `IconButton`, `LinkButton`, `NavLink` |
| `forms.py` | `Label`, `Dropdown`, `Checkbox`, `CheckboxRow` |
| `overlays.py` | `Modal`, `ModalTrigger`, `photo_thumb`, `photo_overlay_script` |
| `debug_overlay.py` | in-page "BUG" reporter: client assets + issue bundle writer |

## Install

```bash
git clone https://github.com/SilasK/fh-ui-wrappers
cd fh-ui-wrappers
pip install -e .
```

Dependencies: `python-fasthtml`, `monsterui`, `pyyaml`.

## Quick start

```python
from fasthtml.common import *
from monsterui.all import Theme, ThemeRadii, ThemeShadows
from fh_ui_wrappers import (
    Button, IconButton, Dropdown, Checkbox, CheckboxRow,
    Modal, ModalTrigger, ModalCloseButton,
    photo_thumb, photo_overlay_script,
)

hdrs = (
    *Theme.blue.headers(radii=ThemeRadii.lg, shadows=ThemeShadows.lg),
    Script(src="https://cdn.jsdelivr.net/npm/franken-ui@2.0.0/dist/js/icon.iife.js",
           type="module"),
    photo_overlay_script(),
)

app, rt = fast_app(hdrs=hdrs, pico=False)

@rt("/")
def get():
    return Titled(
        "Example",
        Button("Enregistrer", submit=True),
        IconButton("trash", label="Supprimer", variant="danger"),
        Dropdown({"a": "Groupe A", "b": "Groupe B"}, name="group",
                 placeholder="Choisir…"),
        Checkbox(name="paid", label="Payé"),
    )

serve()
```

Run the full demo:

```bash
python examples/demo.py
```

## Buttons

`Button` wraps `cls="uk-btn uk-btn-*"` and the icon + label pattern.

```python
Button("Enregistrer", submit=True)
Button("Supprimer", variant="danger", hx_post="/delete")
Button("Planifier", icon="calendar", **{"uk-toggle": "target: #plan-modal"})
Button("Petit", size="sm", variant="secondary")
```

Variants: `primary`, `secondary`, `danger`, `destructive`, `ghost`,
`default`, `text`, `link`, `icon`. Sizes: `xs`, `sm`, `lg`, `xl`.

`Button` defaults to `type="button"` so action buttons never submit a form by
accident. Pass `submit=True` for real submit buttons.

```python
IconButton("camera", label="Prendre une photo")
IconButton("plus", text="Ajouter", variant="primary", size="sm")
LinkButton("Retour", href="/admin", icon="arrow-left", variant="ghost")
NavLink("Tableau de bord", "/admin", active=True, icon="home")
```

`IconButton` sets `aria-label` and `title` from `label`, so icon-only buttons
stay accessible.

## Dropdowns

`Dropdown` accepts a dict, `[(value, label), ...]`, a list of strings, or
objects:

```python
Dropdown({"a": "Groupe A", "b": "Groupe B"}, name="group", value="a")

Dropdown(groups, name="group_id", value_attr="group_id", label_attr="name",
         placeholder="Choisir un groupe…")

Dropdown(options, name="date", native=True, cls="uk-select w-44")
```

Two MonsterUI gotchas are handled for you:

1. **`hx-trigger` must be passed as `hx_trigger`.** MonsterUI rewrites the
   underscore kwarg to `uk-select:input from:#id`; a literal `hx-trigger` string
   bypasses the bridge and silently degrades to `delay` with no event. The
   wrapper translates it.
2. **Sometimes a native `<select>` is safer.** MonsterUI's `Select` renders a
   JS custom element that carries `name` on the wrapper; use `native=True` for
   forms where the selected value must be submitted reliably.

## Checkboxes

```python
Checkbox(name="paid", label="Payé", checked=True)

CheckboxRow(
    "group_ids", group.group_id, group.name,
    description=f"— {headcount} bénéficiaires",
    checked=eligible,
    disabled=not eligible,
    extra=date_select,
)
```

`CheckboxRow` produces the bold title + muted description + optional right-hand
slot layout used in the "Planifier maintenant" modal.

`include_hidden=True` adds a hidden empty field so an unchecked single boolean
still submits `name=""`. Do not use it for repeated checkbox names.

## Overlays

### Photo viewer

```python
# once, in fast_app(hdrs=...)
photo_overlay_script()

# anywhere
photo_thumb("/photos/portrait.jpg", alt="Portrait")
```

Click opens a full-screen viewer; wheel zooms, Escape or a click on the
backdrop closes it.

### Modal

```python
ModalTrigger("Planifier maintenant", target="plan-modal", icon="calendar")

Modal(
    Form(...),
    title="Planifier les distributions",
    modal_id="plan-modal",
    footer=ModalCloseButton("Annuler"),
)
```

### Debug overlay (issue reporter)

A "BUG" tab on the right edge opens a panel that captures a screenshot, the
DOM, the browser console and the recent server log into
`debug/issues/<timestamp>-<slug>/`.

```python
from fh_ui_wrappers import DEBUG_OVERLAY_STYLE, debug_overlay_script

hdrs = (..., DEBUG_OVERLAY_STYLE, debug_overlay_script())
```

Register the two endpoints (see `examples/debug_routes.py`):

```python
from examples.debug_routes import register_debug_overlay
register_debug_overlay(rt, base_dir=Path("debug/issues"), log_dir=Path("logs"),
                       is_admin=lambda session: bool(session.get("admin")))
```

`DEBUG_OVERLAY=0` disables the tab; `DEBUG_OVERLAY=all` offers it to every
visitor (dev only). Without `is_admin` every visitor can submit.

## Design notes

- **Plain labels.** MonsterUI's `Label` renders a `uk-label` badge. `Label` here
  renders a plain `<label>` so form labels are not coloured pills.
- **`uk-btn` classes, not MonsterUI's `Button`.** MonsterUI's `Button` adds
  `uk-btn` itself but forces a default variant; the wrappers give you an
  explicit variant and a safe default `type`.
- **Copy, don't import, if you prefer.** The modules have no internal magic.
  Copy the function you need into your project and delete the rest.

## Extracted from

PartageRivieraDB (`utils/ui_components.py`, `utils/layout.py`,
`utils/debug_overlay.py` and the admin route modules). The patterns were kept
behaviourally identical; names and docstrings were cleaned up for reuse.

## License

MIT — see [LICENSE](LICENSE).
