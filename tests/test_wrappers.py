"""Smoke tests: every wrapper renders, and the tricky bits stay fixed."""

from fasthtml.common import to_xml

from fh_ui_wrappers import (
    Button,
    Checkbox,
    CheckboxRow,
    Dropdown,
    IconButton,
    Label,
    Modal,
    ModalTrigger,
    photo_thumb,
)
from fh_ui_wrappers.debug_overlay import debug_overlay_headers


def html(component):
    return to_xml(component)


def test_button_defaults_to_type_button():
    assert 'type="button"' in html(Button("Action"))
    assert 'type="submit"' in html(Button("Save", submit=True))
    assert "uk-btn-danger" in html(Button("Delete", variant="danger"))


def test_icon_button_is_accessible():
    markup = html(IconButton("trash", label="Supprimer", variant="danger"))
    assert 'aria-label="Supprimer"' in markup
    assert 'title="Supprimer"' in markup


def test_dropdown_selects_value_and_translates_hx_trigger():
    markup = html(
        Dropdown(
            {"a": "Groupe A", "b": "Groupe B"},
            name="group",
            value="b",
            placeholder="Choisir…",
            **{"hx-trigger": "change"},
        )
    )
    assert '<option value="b" selected>Groupe B</option>' in markup
    assert "uk-select:input from:#" in markup


def test_native_dropdown_is_a_real_select():
    markup = html(Dropdown([("a", "A")], name="g", native=True))
    assert markup.startswith("<select")
    assert 'name="g"' in markup


def test_checkbox_row_renders_description():
    markup = html(CheckboxRow("g", "x", "Groupe X", description="— 12"))
    assert "uk-checkbox" in markup
    assert "Groupe X" in markup
    assert "— 12" in markup


def test_label_is_not_a_pill():
    assert "uk-label" not in html(Label("Nom", **{"for": "name"}))


def test_modal_and_photo_overlay_helpers():
    assert "uk-modal" in html(Modal("Body", title="Title", modal_id="m"))
    assert "uk-toggle" in html(ModalTrigger("Open", target="m"))
    assert "openPhotoOverlay(this.src)" in html(photo_thumb("/x.jpg"))


def test_debug_overlay_urls_are_configurable():
    _, script = debug_overlay_headers("/c", "/i")
    markup = html(script)
    assert "/c" in markup and "/i" in markup
    assert "__CONFIG_URL__" not in markup
    assert "__ISSUE_URL__" not in markup


def test_checkbox_hidden_field():
    markup = html(Checkbox(name="paid", label="Payé", include_hidden=True))
    assert 'type="hidden"' in markup
