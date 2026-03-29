# SPDX-License-Identifier: LGPL-2.1-or-later
"""Compatibility wrapper for FontChanger's public API."""

from fontchanger import qss
from fontchanger.config import DEFAULT_SIZE, PARAM_PATH, FontConfig
from fontchanger.core import (
    StartupReapplyManager,
    apply,
    apply_saved,
    get_font_families,
    get_sorted_font_families,
    install_startup_hooks,
    main_window,
    remove,
)
from fontchanger.ui import PreferencePage, PreferencePageAdapter

__all__ = [
    "DEFAULT_SIZE",
    "FontConfig",
    "PARAM_PATH",
    "PreferencePage",
    "PreferencePageAdapter",
    "StartupReapplyManager",
    "apply",
    "apply_saved",
    "get_font_families",
    "get_sorted_font_families",
    "install_startup_hooks",
    "main_window",
    "qss",
    "remove",
]
