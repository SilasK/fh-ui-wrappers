"""Smoke tests: every wrapper renders, and the tricky bits stay fixed."""

from pathlib import Path

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
from fh_ui_wrappers.debug_overlay import (
    MAX_ISSUE_CHARS,
    create_issue_bundle,
    debug_overlay_headers,
    recent_log_tail,
    session_reporter,
)


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


def test_dropdown_with_label_uses_labelselect():
    markup = html(Dropdown({"a": "Groupe A"}, name="group", label="Groupe", value="a"))
    assert "uk-form-label" in markup
    assert 'for="group"' in markup
    assert 'name="group"' in markup
    # FormLabel is the form label, not the pill-shaped uk-label.
    assert "uk-label" not in markup


def test_native_labeled_dropdown_links_label():
    markup = html(
        Dropdown([("a", "A")], name="group", label="Groupe", native=True)
    )
    assert '<label for="group"' in markup
    assert "<select" in markup


def test_multiple_forces_native_select():
    markup = html(Dropdown(["a", "b"], name="groups", multiple=True, value=["a"]))
    assert "<select" in markup
    assert "multiple" in markup
    assert "<uk-select" not in markup


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
    assert "__OVERLAY_CSS__" not in markup
    assert "debug-overlay-tab" in markup


def test_session_reporter_extracts_identity():
    assert session_reporter(
        {
            "role": "admin",
            "user_id": "42",
            "email": "admin@example.com",
            "org_slug": "acme",
            "locale": "fr",
        }
    ) == {
        "role": "admin",
        "user_id": "42",
        "email": "admin@example.com",
        "org_slug": "acme",
    }
    assert session_reporter({"role": "reader", "session_slug": "s1", "session_id": "x"}) == {
        "role": "reader",
        "session_slug": "s1",
        "session_id": "x",
    }
    assert session_reporter({}) == {}
    assert session_reporter(None) == {}


def test_issue_bundle_records_reporter_and_caps_description(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    (log_dir / "app.log").write_text("", encoding="utf-8")

    result = create_issue_bundle(
        issue="x" * (MAX_ISSUE_CHARS + 500),
        url="https://example.com/",
        dom="<html></html>",
        console_log="",
        user_agent="pytest",
        log_dir=log_dir,
        base_dir=tmp_path / "issues",
        reporter={"role": "admin", "email": "admin@example.com"},
    )

    issue_md = (Path(result["path"]) / "issue.md").read_text(encoding="utf-8")
    assert "reporter:" in issue_md
    assert "admin@example.com" in issue_md
    body = issue_md.split("Problème:", 1)[1].strip()
    assert len(body) == MAX_ISSUE_CHARS
    assert set(body) == {"x"}


def test_recent_log_tail_drops_stale_entries_and_their_tracebacks(tmp_path):
    from datetime import datetime, timedelta

    now = datetime.now()
    old = (now - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    recent = (now - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
    log = tmp_path / "app.log"
    log.write_text(
        f"{old} - old entry\nstale traceback\n"
        f"{recent},123 - recent entry\nfresh traceback\n",
        encoding="utf-8",
    )

    tail = recent_log_tail(log, minutes=15)

    assert "recent entry" in tail
    assert "fresh traceback" in tail
    assert "stale traceback" not in tail
    assert "old entry" not in tail


def test_issue_bundle_admin_label_is_backwards_compatible(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    result = create_issue_bundle(
        issue="bug",
        url="https://example.com/",
        dom="",
        console_log="",
        user_agent="pytest",
        log_dir=log_dir,
        base_dir=tmp_path / "issues",
        admin="dev",
    )

    issue_md = (Path(result["path"]) / "issue.md").read_text(encoding="utf-8")
    assert "admin: dev" in issue_md



def test_checkbox_hidden_field():
    markup = html(Checkbox(name="paid", label="Payé", include_hidden=True))
    assert 'type="hidden"' in markup
