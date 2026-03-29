# FontChanger — InitGui.py
# Runs at FreeCAD GUI startup.
# SPDX-License-Identifier: LGPL-2.1-or-later
"""
Register the FontChanger preferences page.

This file intentionally stays minimal. FreeCAD's InitGui execution environment
is quirky, so all delayed startup logic lives in font_changer.py, which is a
normal imported Python module with stable globals.
"""

import FreeCAD as App
import FreeCADGui as Gui

import font_changer


try:
    Gui.addPreferencePage(font_changer.PreferencePageAdapter, "Display")
    font_changer.install_startup_hooks()
    App.Console.PrintLog("[FontChanger] Ready.\n")
except Exception as exc:
    App.Console.PrintError(f"[FontChanger] Startup failed: {exc}\n")


class FontChangerStub(Gui.Workbench):
    """Stub class required by package.xml and intentionally never registered."""

    MenuText = "FontChanger"
    ToolTip = "Internal stub"

    def Initialize(self) -> None:
        pass

    def GetClassName(self) -> str:
        return "Gui::PythonWorkbench"
