# SPDX-License-Identifier: LGPL-2.1-or-later
"""Core runtime behavior for FontChanger."""

from functools import lru_cache
from typing import FrozenSet, Optional

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from .config import FontConfig
from .qss import build_qss, split_qss

STARTUP_REAPPLY_DELAYS_MS = (0, 100, 500, 1500, 3000, 6000)
FALLBACK_FONT_CANDIDATES = (
    "Noto Sans",
    "DejaVu Sans",
    "Arial",
    "Helvetica",
    "Liberation Sans",
    "Ubuntu",
    "Sans Serif",
)

_startup_reapply_manager: Optional["StartupReapplyManager"] = None
_warned_missing_families: set[str] = set()


def main_window() -> Optional[QtWidgets.QMainWindow]:
    """Return the FreeCAD main window when available."""

    return Gui.getMainWindow()


@lru_cache(maxsize=1)
def get_font_families() -> FrozenSet[str]:
    """Return available font family names."""

    return frozenset(QtGui.QFontDatabase.families())


@lru_cache(maxsize=1)
def get_sorted_font_families() -> tuple[str, ...]:
    """Return available font families sorted alphabetically."""

    return tuple(sorted(get_font_families()))


def resolve_font_family(requested_family: str) -> tuple[str, bool]:
    """Return (family_to_apply, used_fallback) for the current system."""

    families = get_font_families()
    if not families:
        return "", False

    if requested_family in families:
        return requested_family, False

    lower_map = {family.casefold(): family for family in families}
    case_insensitive_match = lower_map.get(requested_family.casefold())
    if case_insensitive_match:
        return case_insensitive_match, False

    app = QtWidgets.QApplication.instance()
    if app:
        app_family = app.font().family().strip()
        if app_family:
            fallback_family = lower_map.get(app_family.casefold())
            if fallback_family:
                return fallback_family, True

    for candidate in FALLBACK_FONT_CANDIDATES:
        fallback_family = lower_map.get(candidate.casefold())
        if fallback_family:
            return fallback_family, True

    return get_sorted_font_families()[0], True


def apply(
    family: str,
    size: int,
    color: str = "",
) -> bool:
    """Apply the requested font override to the live FreeCAD UI."""

    window = main_window()
    if not window:
        return False

    resolved_family, used_fallback = resolve_font_family(family)
    if not resolved_family:
        App.Console.PrintWarning("[FontChanger] No usable fonts found.\n")
        return False

    if used_fallback and family not in _warned_missing_families:
        App.Console.PrintWarning(
            f'[FontChanger] "{family}" not found. Using "{resolved_family}" instead.\n'
        )
        _warned_missing_families.add(family)

    base_sheet, current_block = split_qss(window.styleSheet())
    desired_block = build_qss(resolved_family, size, color)
    if current_block == desired_block:
        return True

    window.setStyleSheet(base_sheet + desired_block)
    App.Console.PrintMessage(f"[FontChanger] Applied {resolved_family} {size}pt\n")
    return True


def remove() -> None:
    """Remove the FontChanger stylesheet block from the live UI."""

    window = main_window()
    if not window:
        return

    base_sheet, current_block = split_qss(window.styleSheet())
    if current_block:
        window.setStyleSheet(base_sheet)


def apply_saved() -> None:
    """Apply the saved configuration if FontChanger is enabled."""

    config = FontConfig.load()
    if config.enabled and config.family:
        apply(config.family, config.size, config.color)


class StartupReapplyManager(QtCore.QObject):
    """Re-apply saved settings after late startup/theme stylesheet updates."""

    def __init__(self, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self._workbench_hooked = False

    def start(self) -> None:
        for delay_ms in STARTUP_REAPPLY_DELAYS_MS:
            QtCore.QTimer.singleShot(delay_ms, self._bind_and_apply)

    def _bind_and_apply(self) -> None:
        self._bind_workbench_signal()
        self._apply_saved_safe()

    def _bind_workbench_signal(self) -> None:
        if self._workbench_hooked:
            return

        window = main_window()
        if not window:
            return

        try:
            window.workbenchActivated.connect(self._apply_saved_safe)
            self._workbench_hooked = True
        except Exception as exc:
            App.Console.PrintWarning(
                f"[FontChanger] Could not hook workbenchActivated, continuing without it: {exc}\n"
            )

    def _apply_saved_safe(self, *_args: object) -> None:
        try:
            apply_saved()
        except Exception as exc:
            App.Console.PrintError(f"[FontChanger] apply_saved failed: {exc}\n")


def install_startup_hooks() -> None:
    """Install startup re-apply hooks once per FreeCAD session."""

    global _startup_reapply_manager

    if _startup_reapply_manager is not None:
        return

    _startup_reapply_manager = StartupReapplyManager()
    _startup_reapply_manager.start()
