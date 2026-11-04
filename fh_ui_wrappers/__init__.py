"""Reusable FastHTML + MonsterUI UI wrappers.

Extracted and generalised from the PartageRiviera app. Copy this package into a
project, or add the repository as a dependency, and import the pieces you need::

    from fh_ui_wrappers import Button, IconButton, Dropdown, Checkbox
    from fh_ui_wrappers import Modal, ModalTrigger, photo_thumb, photo_overlay_script
    from fh_ui_wrappers import DEBUG_OVERLAY_STYLE, debug_overlay_script
"""

from .buttons import (
    BUTTON_SIZES,
    BUTTON_VARIANTS,
    Button,
    IconButton,
    LinkButton,
    NavLink,
)
from .debug_overlay import (
    DEBUG_OVERLAY_STYLE,
    create_issue_bundle,
    debug_overlay_enabled,
    debug_overlay_headers,
    debug_overlay_public,
    debug_overlay_script,
    recent_server_log,
)
from .forms import Checkbox, CheckboxRow, Dropdown, Label
from .overlays import (
    PHOTO_OVERLAY_SCRIPT,
    Modal,
    ModalCloseButton,
    ModalTitle,
    ModalTrigger,
    photo_overlay_script,
    photo_thumb,
)

__all__ = [
    "BUTTON_SIZES",
    "BUTTON_VARIANTS",
    "Button",
    "Checkbox",
    "CheckboxRow",
    "DEBUG_OVERLAY_STYLE",
    "Dropdown",
    "IconButton",
    "Label",
    "LinkButton",
    "Modal",
    "ModalCloseButton",
    "ModalTitle",
    "ModalTrigger",
    "NavLink",
    "PHOTO_OVERLAY_SCRIPT",
    "create_issue_bundle",
    "debug_overlay_enabled",
    "debug_overlay_headers",
    "debug_overlay_public",
    "debug_overlay_script",
    "photo_overlay_script",
    "photo_thumb",
    "recent_server_log",
]
