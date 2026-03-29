# SPDX-License-Identifier: LGPL-2.1-or-later
"""Compatibility wrapper for FontBook's public API."""

from fontbook import qss
from fontbook.config import DEFAULT_SIZE, PARAM_PATH, FontConfig
from fontbook.core import (
    StartupReapplyManager,
    apply,
    apply_saved,
    get_font_families,
    get_sorted_font_families,
    install_startup_hooks,
    main_window,
    remove,
)
from fontbook.ui import PreferencePage, PreferencePageAdapter

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
