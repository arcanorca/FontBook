# SPDX-License-Identifier: LGPL-2.1-or-later
"""Preference page widgets for FontBook."""

import html
from typing import Optional

from PySide import QtCore, QtGui, QtWidgets

from .config import DEFAULT_SIZE, FontConfig
from .core import apply, get_sorted_font_families, remove

PREVIEW_BOX_QSS = "padding:8px;border:1px solid #495057;border-radius:4px;"
SWATCH_BASE_QSS = "border:1px solid #495057;border-radius:4px;"


def _tr(text: str) -> str:
    """Translate FontBook UI text through Qt when available."""

    translate = getattr(QtCore.QCoreApplication, "translate", None)
    if callable(translate):
        return translate("FontBook", text)
    return text


def _normalize_dialog_text(text: str) -> str:
    """Normalize mnemonic-heavy dialog labels for comparison."""

    return text.replace("&", "").replace(":", "").strip().casefold()


def _dialog_text_variants(dialog: QtWidgets.QColorDialog, text: str) -> set[str]:
    """Return translated variants for Qt's built-in color-dialog labels."""

    variants = {text}

    dialog_translate = getattr(dialog, "tr", None)
    if callable(dialog_translate):
        variants.add(dialog_translate(text))

    core_translate = getattr(QtCore.QCoreApplication, "translate", None)
    if callable(core_translate):
        variants.add(core_translate("QColorDialog", text))

    return {_normalize_dialog_text(variant) for variant in variants if variant}


def pick_color(initial_hex: str, parent: QtWidgets.QWidget) -> str:
    """Return the user-selected color, or an empty string if cancelled."""

    initial = QtGui.QColor(initial_hex or "#dee2e6")
    dialog = QtWidgets.QColorDialog(initial, parent)
    dialog.setWindowTitle(_tr("Pick font color"))
    dialog.setOption(QtWidgets.QColorDialog.DontUseNativeDialog, True)
    _hide_custom_colors_section(dialog)
    QtCore.QTimer.singleShot(0, lambda dlg=dialog: _hide_custom_colors_section(dlg))

    exec_dialog = getattr(dialog, "exec_", None) or getattr(dialog, "exec")
    if exec_dialog() != QtWidgets.QDialog.Accepted:
        return ""

    color = dialog.selectedColor()
    return color.name() if color.isValid() else ""


def _hide_custom_colors_section(dialog: QtWidgets.QColorDialog) -> None:
    """Hide the custom-colors controls in the non-native Qt color dialog."""

    def find_layout_containing(layout: QtWidgets.QLayout, target: QtWidgets.QWidget) -> Optional[QtWidgets.QLayout]:
        if not layout:
            return None
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() == target:
                return layout
            elif item.layout():
                res = find_layout_containing(item.layout(), target)
                if res:
                    return res
        return None

    custom_label: Optional[QtWidgets.QWidget] = None
    for widget in dialog.findChildren(QtWidgets.QWidget):
        text = ""
        if hasattr(widget, "text"):
            try:
                text = widget.text()
            except Exception:
                pass
        
        normalized = _normalize_dialog_text(text)
        if normalized == _normalize_dialog_text("&Custom colors"):
            custom_label = widget
            break

    if custom_label and dialog.layout():
        parent_layout = find_layout_containing(dialog.layout(), custom_label)
        if parent_layout:
            hide_next = False
            for i in range(parent_layout.count()):
                item = parent_layout.itemAt(i)
                w = item.widget()
                if not w:
                    continue
                
                if w == custom_label:
                    hide_next = True
                    w.hide()
                    continue
                
                if hide_next:
                    text = ""
                    if hasattr(w, "text"):
                        try:
                            text = w.text()
                        except Exception:
                            pass
                    
                    normalized = _normalize_dialog_text(text)
                    w.hide()
                    
                    # Stop hiding once we hit the "Add to Custom Colors" button
                    if normalized == _normalize_dialog_text("&Add to Custom Colors"):
                        hide_next = False


class PreferencePage(QtWidgets.QWidget):
    """Edit -> Preferences -> Display -> FontBook."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_tr("FontBook"))

        self._color = ""
        self._preview_state: Optional[tuple[str, int, str]] = None

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        self.enable_checkbox = QtWidgets.QCheckBox(_tr("Enable custom UI font"))
        self.enable_checkbox.setChecked(False)
        root.addWidget(self.enable_checkbox)

        settings_group = QtWidgets.QGroupBox(_tr("Font Settings"))
        settings_form = QtWidgets.QFormLayout(settings_group)
        settings_form.setContentsMargins(10, 14, 10, 10)

        self.font_combo = QtWidgets.QComboBox()
        self.font_combo.setEditable(True)
        self.font_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.font_combo.setMaxVisibleItems(12)
        completer = self.font_combo.completer()
        if completer:
            completer.setFilterMode(QtCore.Qt.MatchContains)
            completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        settings_form.addRow(_tr("Font:"), self.font_combo)

        self.size_spin = QtWidgets.QSpinBox()
        self.size_spin.setRange(6, 32)
        self.size_spin.setSuffix(_tr(" pt"))
        settings_form.addRow(_tr("Size:"), self.size_spin)

        color_row = QtWidgets.QHBoxLayout()
        self.color_swatch = QtWidgets.QPushButton()
        self.color_swatch.setFixedSize(28, 28)
        self.color_swatch.setCursor(QtCore.Qt.PointingHandCursor)
        self.color_swatch.clicked.connect(self._pick_color)
        color_row.addWidget(self.color_swatch)

        self.reset_button = QtWidgets.QPushButton(_tr("Reset"))
        self.reset_button.setObjectName("FontBookResetButton")
        self.reset_button.clicked.connect(self._reset_color)
        color_row.addWidget(self.reset_button)
        color_row.addStretch()
        settings_form.addRow(_tr("Color:"), color_row)

        root.addWidget(settings_group)

        preview_group = QtWidgets.QGroupBox(_tr("Preview"))
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(10, 14, 10, 10)

        preview_lines = (
            f"{_tr('The quick brown fox jumps over the lazy dog.')}\n"
            "0123456789  ABCDEFGHIJKLM  abcdefghijklm\n"
            "{}[]()<>  !=  <=  >=  =>  ->  |>"
        )
        self._preview_html_body = "<br/>".join(
            html.escape(line) for line in preview_lines.splitlines()
        )

        self.preview_label = QtWidgets.QLabel(preview_lines)
        self.preview_label.setWordWrap(True)
        self.preview_label.setMinimumHeight(72)
        self.preview_label.setStyleSheet(PREVIEW_BOX_QSS)
        preview_layout.addWidget(self.preview_label)

        root.addWidget(preview_group)
        root.addStretch()

        self.enable_checkbox.toggled.connect(self._toggle_controls)
        self.font_combo.currentIndexChanged.connect(self._refresh_preview)
        self.font_combo.editTextChanged.connect(self._refresh_preview)
        self.size_spin.valueChanged.connect(self._refresh_preview)

        self._toggle_controls(False)

    def loadSettings(self) -> None:
        self._populate_fonts()
        config = FontConfig.load()

        self.enable_checkbox.blockSignals(True)
        self.font_combo.blockSignals(True)
        self.size_spin.blockSignals(True)

        self.enable_checkbox.setChecked(config.enabled)
        self._set_font_text(config.family)
        self.size_spin.setValue(config.size or DEFAULT_SIZE)

        self.enable_checkbox.blockSignals(False)
        self.font_combo.blockSignals(False)
        self.size_spin.blockSignals(False)

        self._set_color(config.color)
        self._toggle_controls(config.enabled)
        self._refresh_preview()

    def saveSettings(self) -> None:
        config = FontConfig(
            family=self.font_combo.currentText(),
            size=self.size_spin.value(),
            color=self._color,
            enabled=self.enable_checkbox.isChecked(),
        )
        config.save()

        if config.enabled and config.family:
            apply(config.family, config.size, config.color)
        else:
            remove()

    def _populate_fonts(self) -> None:
        if self.font_combo.count() > 0:
            return
        self.font_combo.blockSignals(True)
        self.font_combo.addItems(get_sorted_font_families())
        self.font_combo.blockSignals(False)

    def _set_font_text(self, family: str) -> None:
        if not family:
            return
        index = self.font_combo.findText(family)
        if index >= 0:
            self.font_combo.setCurrentIndex(index)
        else:
            self.font_combo.setEditText(family)

    def _toggle_controls(self, enabled: bool) -> None:
        for widget in (
            self.font_combo,
            self.size_spin,
            self.color_swatch,
            self.reset_button,
        ):
            widget.setEnabled(enabled)

    def _refresh_preview(self, *_args: object) -> None:
        state = (self.font_combo.currentText(), self.size_spin.value(), self._color)
        if state == self._preview_state:
            return

        styles = [f"font-size: {self.size_spin.value()}pt;"]
        if self.font_combo.currentText():
            styles.append(f'font-family: "{self.font_combo.currentText()}";')
        if self._color:
            styles.append(f"color: {self._color};")

        style_attr = html.escape(" ".join(styles), quote=True)
        self.preview_label.setTextFormat(QtCore.Qt.RichText)
        self.preview_label.setText(f'<div style="{style_attr}">{self._preview_html_body}</div>')
        self._preview_state = state

    def _pick_color(self) -> None:
        color = pick_color(self._color, self)
        if color:
            self._set_color(color)
            self._refresh_preview()

    def _reset_color(self) -> None:
        self._set_color("")
        self._refresh_preview()

    def _set_color(self, color: str) -> None:
        self._color = color
        self._preview_state = None
        background = color if color else "transparent"
        self.color_swatch.setStyleSheet(f"background-color:{background};{SWATCH_BASE_QSS}")


class PreferencePageAdapter:
    """FreeCAD preference-page adapter exposing the ``form`` attribute."""

    def __init__(self) -> None:
        self.form = PreferencePage()

    def loadSettings(self) -> None:
        self.form.loadSettings()

    def saveSettings(self) -> None:
        self.form.saveSettings()
