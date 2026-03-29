# SPDX-License-Identifier: LGPL-2.1-or-later
"""Pure QSS parsing and generation for FontBook."""

import re
from typing import Pattern

QSS_TAG = "/* FontBook */"
QSS_START_TAG = "/* FontBook:start */"
QSS_END_TAG = "/* FontBook:end */"

QSS_BLOCK_RE: Pattern[str] = re.compile(
    r"\n?" + re.escape(QSS_START_TAG) + r".*?" + re.escape(QSS_END_TAG) + r"\n?",
    flags=re.DOTALL,
)

LEGACY_QSS_BLOCK_RE: Pattern[str] = re.compile(
    r"\n?" + re.escape(QSS_TAG) + r".*?" + re.escape(QSS_TAG) + r"\n?",
    flags=re.DOTALL,
)

QSS_ORPHAN_BLOCK_RE: Pattern[str] = re.compile(
    r"\n?" + re.escape(QSS_START_TAG) + r".*\Z",
    flags=re.DOTALL,
)

LEGACY_QSS_ORPHAN_BLOCK_RE: Pattern[str] = re.compile(
    r"\n?" + re.escape(QSS_TAG) + r".*\Z",
    flags=re.DOTALL,
)

# Global color overrides cover the common UI chrome the addon is expected to
# recolor. More complex FreeCAD panels still get their own targeted rules below
# so we can keep value editors and recovery controls readable.
COLOR_TARGETS = ",".join(
    [
        "QLabel",
        "QAbstractButton",
        "QListView",
        "QListView::item",
        "QTreeView",
        "QTreeView::item",
        "QGroupBox::title",
        "QMenuBar::item",
        "QMenu::item",
        "QTabBar::tab",
        "Gui--WorkbenchComboBox",
    ]
)

PREFERENCES_TEXT_TARGETS = ",".join(
    [
        "QDialog#Gui__Dialog__DlgPreferences QLabel",
        "QDialog#Gui__Dialog__DlgPreferences QGroupBox::title",
        "QDialog#Gui__Dialog__DlgPreferences QCheckBox",
        "QDialog#Gui__Dialog__DlgPreferences QRadioButton",
        "QDialog#Gui__Dialog__DlgPreferences QListView",
        "QDialog#Gui__Dialog__DlgPreferences QListView::item",
        "QDialog#Gui__Dialog__DlgPreferences QTreeView#groupsTreeView",
        "QDialog#Gui__Dialog__DlgPreferences QTreeView#groupsTreeView::item",
        "QDialog#Gui__Dialog__DlgPreferences QTabBar::tab",
    ]
)

COLOR_DIALOG_TEXT_TARGETS = "QColorDialog QLabel"

WORKBENCH_POPUP_TARGETS = ",".join(
    [
        "QToolBar > Gui--WorkbenchComboBox QAbstractItemView",
        "QToolBar > Gui--WorkbenchComboBox QAbstractItemView::item",
    ]
)

TREE_PANEL_TEXT_TARGETS = ",".join(
    [
        "Gui--TreePanel QTreeView",
        "Gui--TreePanel QTreeView::item",
    ]
)

PROPERTY_EDITOR_ROOT_TARGETS = "Gui--PropertyEditor--PropertyEditor"

PROPERTY_EDITOR_LEFT_ITEM_TARGETS = "Gui--PropertyEditor--PropertyEditor::item"

PROPERTY_EDITOR_VALUE_TARGETS = ",".join(
    [
        "Gui--PropertyEditor--PropertyEditor QLineEdit",
        "Gui--PropertyEditor--PropertyEditor QAbstractSpinBox",
        "Gui--PropertyEditor--PropertyEditor QComboBox",
        "Gui--PropertyEditor--PropertyEditor QComboBox QAbstractItemView",
        "Gui--PropertyEditor--PropertyEditor QComboBox QAbstractItemView::item",
    ]
)

PROPERTY_EDITOR_OVERLAY_VALUE_TARGETS = (
    "Gui--PropertyEditor--PropertyEditor > QWidget > QWidget > QLabel"
)


def build_qss(family: str, size: int, color: str = "") -> str:
    """Return the tagged stylesheet block managed by FontBook."""

    rules = f'QWidget {{ font-family: "{family}"; font-size: {size}pt; }}'
    if color:
        rules += f"\n{COLOR_TARGETS} {{ color: {color}; }}"
        rules += f"\n{PREFERENCES_TEXT_TARGETS} {{ color: {color}; }}"
        rules += f"\n{COLOR_DIALOG_TEXT_TARGETS} {{ color: palette(windowText); }}"
        rules += f"\n{WORKBENCH_POPUP_TARGETS} {{ color: {color}; }}"
        rules += f"\n{TREE_PANEL_TEXT_TARGETS} {{ color: {color}; }}"
        rules += (
            f"\n{PROPERTY_EDITOR_ROOT_TARGETS} "
            f"{{ color: {color}; qproperty-groupTextColor: {color}; }}"
        )
        rules += f"\n{PROPERTY_EDITOR_LEFT_ITEM_TARGETS} {{ color: {color}; }}"
        rules += f"\n{PROPERTY_EDITOR_VALUE_TARGETS} {{ color: palette(text); }}"
        rules += (
            f"\n{PROPERTY_EDITOR_OVERLAY_VALUE_TARGETS} "
            "{ color: palette(text); background-color: palette(base); }"
        )
    return f"\n{QSS_START_TAG}\n{rules}\n{QSS_END_TAG}\n"


def split_qss(sheet: str) -> tuple[str, str]:
    """Return (sheet_without_fontbook_blocks, first_fontbook_block_or_empty)."""

    matches = []
    for pattern in (QSS_BLOCK_RE, LEGACY_QSS_BLOCK_RE):
        match = pattern.search(sheet)
        if match:
            matches.append(match)

    current_block = min(matches, key=lambda match: match.start()).group(0) if matches else ""

    base_sheet = sheet
    for pattern in (
        QSS_BLOCK_RE,
        LEGACY_QSS_BLOCK_RE,
        QSS_ORPHAN_BLOCK_RE,
        LEGACY_QSS_ORPHAN_BLOCK_RE,
    ):
        base_sheet = pattern.sub("", base_sheet)
    return base_sheet, current_block
