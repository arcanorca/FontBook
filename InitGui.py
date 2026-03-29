# FontBook — InitGui.py
# Runs at FreeCAD GUI startup.
# SPDX-License-Identifier: LGPL-2.1-or-later
"""
Register the FontBook preferences page.

This file intentionally stays minimal. FreeCAD's InitGui execution environment
is quirky, so all delayed startup logic lives in font_book.py, which is a
normal imported Python module with stable globals.
"""

import FreeCAD as App
import FreeCADGui as Gui

import font_book


try:
    Gui.addPreferencePage(font_book.PreferencePageAdapter, "Display")
    font_book.install_startup_hooks()
    App.Console.PrintLog("[FontBook] Ready.\n")
except Exception as exc:
    App.Console.PrintError(f"[FontBook] Startup failed: {exc}\n")


class FontBookStub(Gui.Workbench):
    """Stub class required by package.xml and intentionally never registered."""

    MenuText = "FontBook"
    ToolTip = "Internal stub"

    def Initialize(self) -> None:
        pass

    def GetClassName(self) -> str:
        return "Gui::PythonWorkbench"
