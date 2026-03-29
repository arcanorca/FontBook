# SPDX-License-Identifier: LGPL-2.1-or-later
"""Persistence primitives for FontBook."""

from dataclasses import dataclass

import FreeCAD as App

PARAM_PATH = "User parameter:BaseApp/Preferences/Mod/FontBook"
DEFAULT_SIZE = 10


@dataclass
class FontConfig:
    """Persistent user settings for FontBook."""

    family: str = ""
    size: int = DEFAULT_SIZE
    color: str = ""
    enabled: bool = False

    @classmethod
    def load(cls) -> "FontConfig":
        prefs = App.ParamGet(PARAM_PATH)
        return cls(
            family=prefs.GetString("FontFamily", ""),
            size=prefs.GetInt("FontSize", DEFAULT_SIZE),
            color=prefs.GetString("FontColor", ""),
            enabled=prefs.GetBool("Enabled", False),
        )

    def save(self) -> None:
        prefs = App.ParamGet(PARAM_PATH)
        prefs.SetString("FontFamily", self.family)
        prefs.SetInt("FontSize", self.size)
        prefs.SetString("FontColor", self.color)
        prefs.SetBool("Enabled", self.enabled)

        flush = getattr(App, "SaveParameter", None)
        if callable(flush):
            flush()
