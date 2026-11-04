"""Runnable demo for fh_ui_wrappers.

    python examples/demo.py

Then open http://localhost:5001 (FastHTML's default port).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fasthtml.common import *  # noqa: F401,F403
from monsterui.all import (  # noqa: F401
    Container,
    Theme,
    ThemeRadii,
    ThemeShadows,
)

from examples.debug_routes import register_debug_overlay
from fh_ui_wrappers import (
    DEBUG_OVERLAY_STYLE,
    Button,
    Checkbox,
    CheckboxRow,
    Dropdown,
    IconButton,
    LinkButton,
    Modal,
    ModalCloseButton,
    ModalTrigger,
    NavLink,
    debug_overlay_script,
    photo_overlay_script,
    photo_thumb,
)

hdrs = (
    *Theme.blue.headers(radii=ThemeRadii.lg, shadows=ThemeShadows.lg),
    Script(
        src="https://cdn.jsdelivr.net/npm/franken-ui@2.0.0/dist/js/icon.iife.js",
        type="module",
    ),
    photo_overlay_script(),
    DEBUG_OVERLAY_STYLE,
    debug_overlay_script(),
)

app, rt = fast_app(hdrs=hdrs, pico=False, secret_key="demo-only-secret")
register_debug_overlay(rt, base_dir=ROOT / "debug" / "issues")

GROUPS = [
    ("clarens", "Clarens — Jeudi"),
    ("passerelle_lundi", "La Passerelle — Lundi"),
    ("passerelle_mardi", "La Passerelle — Mardi"),
]

PHOTO = "data:image/svg+xml," + quote(
    """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420">
    <rect width="640" height="420" fill="#dbeafe"/>
    <circle cx="320" cy="180" r="90" fill="#93c5fd"/>
    <rect x="200" y="280" width="240" height="90" rx="16" fill="#60a5fa"/>
    <text x="320" y="400" font-family="sans-serif" font-size="22"
          text-anchor="middle" fill="#1e3a8a">photo de démonstration</text>
    </svg>"""
)

SECTION = "mb-10 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
GRID = "flex flex-wrap items-center gap-3"


def section(title, *content):
    return Section(H2(title, cls="mb-4 text-xl font-bold"), *content, cls=SECTION)


@rt("/")
def get():
    return (
        Title("fh-ui-wrappers demo"),
        Main(
            Container(
                Div(
                    NavLink("Accueil", "/", active=True, icon="home"),
                    NavLink(
                        "Dépôt GitHub",
                        "https://github.com/SilasK/fh-ui-wrappers",
                        icon="github",
                    ),
                    cls="mb-8 flex items-center gap-2 border-b border-gray-200 pb-4",
                ),
                H1("fh-ui-wrappers", cls="mb-2 text-3xl font-bold"),
                P(
                    "Wrappers FastHTML + MonsterUI extraits de PartageRivieraDB.",
                    cls="mb-8 text-gray-600",
                ),
                section(
                    "Boutons",
                    Div(
                        Button("Primaire"),
                        Button("Secondaire", variant="secondary"),
                        Button("Danger", variant="danger"),
                        Button("Ghost", variant="ghost"),
                        Button("Avec icône", icon="plus"),
                        LinkButton("Retour", href="/", icon="arrow-left", variant="ghost"),
                        cls=GRID,
                    ),
                    Div(
                        IconButton("camera", label="Prendre une photo"),
                        IconButton("trash", label="Supprimer", variant="danger"),
                        IconButton("plus", text="Ajouter", variant="primary", size="sm"),
                        cls=GRID + " mt-3",
                    ),
                ),
                section(
                    "Dropdowns",
                    Form(
                        Div(
                            Label("MonsterUI (bridge uk-select)", cls="mb-1 block text-sm font-medium"),
                            Dropdown(
                                GROUPS,
                                name="group",
                                placeholder="Choisir un groupe…",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Label("Natif (soumission fiable)", cls="mb-1 block text-sm font-medium"),
                            Dropdown(
                                GROUPS,
                                name="group_native",
                                placeholder="Choisir un groupe…",
                                native=True,
                                cls="uk-select w-64",
                            ),
                        ),
                        cls="max-w-xl",
                    ),
                ),
                section(
                    "Checkboxes",
                    Form(
                        Checkbox(name="paid", label="Payé", value="1"),
                        Div(
                            CheckboxRow(
                                "group_ids",
                                "clarens",
                                "Clarens",
                                description="— 24 bénéficiaires",
                                checked=True,
                            ),
                            CheckboxRow(
                                "group_ids",
                                "passerelle_lundi",
                                "La Passerelle — Lundi",
                                description="— 18 bénéficiaires",
                                checked=True,
                            ),
                            CheckboxRow(
                                "group_ids",
                                "passerelle_mardi",
                                "La Passerelle — Mardi",
                                description="— groupe complet",
                                disabled=True,
                            ),
                            cls="mt-3 divide-y divide-gray-100",
                        ),
                        Button(
                            "Envoyer",
                            submit=True,
                            cls="mt-4",
                            hx_post="/echo",
                            hx_target="#echo",
                            hx_include="closest form",
                        ),
                        Button(
                            "Envoyer (POST complet)",
                            submit=True,
                            variant="secondary",
                            cls="mt-4 ml-2",
                        ),
                        action="/echo",
                        method="post",
                    ),
                    Pre(
                        "Le résultat du POST apparaît ici (htmx) ou sur une page dédiée.",
                        id="echo",
                        cls="mt-4 overflow-auto rounded-lg bg-gray-50 p-3 text-xs",
                    ),
                ),
                section(
                    "Overlays",
                    Div(
                        ModalTrigger("Ouvrir la modale", target="demo-modal", icon="calendar"),
                        Span("Cliquez sur la photo pour l'overlay zoomable", cls="text-sm text-gray-500"),
                        cls=GRID,
                    ),
                    Div(photo_thumb(PHOTO, alt="Photo de démonstration"), cls="mt-4"),
                    Modal(
                        P("Contenu de la modale. Échap ou le bouton ferment l'overlay."),
                        title="Planifier les distributions",
                        modal_id="demo-modal",
                        footer=ModalCloseButton("Fermer"),
                    ),
                ),
                cls="pb-16",
            )
        ),
    )


@rt("/echo", methods=["POST"])
async def post(request):
    form = await request.form()
    data: dict[str, list[str]] = {}
    for key, value in form.multi_items():
        data.setdefault(key, []).append(str(value))
    return Pre(json.dumps(data, indent=2, ensure_ascii=False), cls="p-6")


serve()
