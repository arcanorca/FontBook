import importlib
import os
import sys
import types
import unittest
from unittest import mock


ADDON_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ADDON_ROOT not in sys.path:
    sys.path.insert(0, ADDON_ROOT)


class FakePrefs:
    def __init__(self, store):
        self.store = store

    def GetString(self, key, default=""):
        return self.store.get(key, default)

    def GetInt(self, key, default=0):
        return self.store.get(key, default)

    def GetBool(self, key, default=False):
        return self.store.get(key, default)

    def SetString(self, key, value):
        self.store[key] = value

    def SetInt(self, key, value):
        self.store[key] = value

    def SetBool(self, key, value):
        self.store[key] = value


class FakeSignal:
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)


class FakeWindow:
    def __init__(self, stylesheet=""):
        self._stylesheet = stylesheet
        self.workbenchActivated = FakeSignal()

    def styleSheet(self):
        return self._stylesheet

    def setStyleSheet(self, stylesheet):
        self._stylesheet = stylesheet


class FakeQObject:
    def __init__(self, parent=None):
        self.parent = parent


class FakeQTimer:
    calls = []

    @staticmethod
    def singleShot(delay_ms, callback):
        FakeQTimer.calls.append((delay_ms, callback))


class FakeFont:
    def __init__(self, family):
        self._family = family

    def family(self):
        return self._family


class FakeApplication:
    _instance = None

    def __init__(self, family="System Sans"):
        self._font = FakeFont(family)
        FakeApplication._instance = self

    @classmethod
    def instance(cls):
        return cls._instance

    def font(self):
        return self._font


class FakeFontDatabase:
    families_value = []

    @staticmethod
    def families():
        return list(FakeFontDatabase.families_value)


def build_fake_environment(
    *,
    store=None,
    families=None,
    app_family="System Sans",
    stylesheet="",
    with_save_parameter=True,
):
    store = {} if store is None else store
    families = [] if families is None else families
    FakeFontDatabase.families_value = list(families)
    FakeApplication._instance = FakeApplication(app_family)
    FakeQTimer.calls = []
    window = FakeWindow(stylesheet)

    console = types.SimpleNamespace(
        PrintMessage=mock.Mock(),
        PrintWarning=mock.Mock(),
        PrintError=mock.Mock(),
    )

    freecad_module = types.ModuleType("FreeCAD")
    freecad_module.Console = console
    freecad_module.ParamGet = lambda _path: FakePrefs(store)
    if with_save_parameter:
        freecad_module.SaveParameter = mock.Mock()

    freecadgui_module = types.ModuleType("FreeCADGui")
    freecadgui_module.getMainWindow = mock.Mock(return_value=window)

    qtcore = types.SimpleNamespace(QObject=FakeQObject, QTimer=FakeQTimer)
    qtgui = types.SimpleNamespace(QFontDatabase=FakeFontDatabase)
    qtwidgets = types.SimpleNamespace(
        QApplication=FakeApplication,
        QMainWindow=FakeWindow,
    )

    pyside_module = types.ModuleType("PySide")
    pyside_module.QtCore = qtcore
    pyside_module.QtGui = qtgui
    pyside_module.QtWidgets = qtwidgets

    return {
        "FreeCAD": freecad_module,
        "FreeCADGui": freecadgui_module,
        "PySide": pyside_module,
        "window": window,
        "console": console,
        "store": store,
    }


def import_runtime_modules(fake_modules):
    module_names = (
        "fontbook.config",
        "fontbook.core",
    )
    for name in module_names:
        sys.modules.pop(name, None)

    with mock.patch.dict(sys.modules, fake_modules):
        config = importlib.import_module("fontbook.config")
        core = importlib.import_module("fontbook.core")
        core.get_font_families.cache_clear()
        core.get_sorted_font_families.cache_clear()
        core._warned_missing_families.clear()
        core._startup_reapply_manager = None
        return config, core


class TestConfig(unittest.TestCase):
    def test_load_reads_persisted_values(self):
        fake_modules = build_fake_environment(
            store={
                "FontFamily": "Ubuntu",
                "FontSize": 13,
                "FontColor": "#ff0000",
                "Enabled": True,
            }
        )
        config, _ = import_runtime_modules(fake_modules)

        loaded = config.FontConfig.load()

        self.assertEqual(loaded.family, "Ubuntu")
        self.assertEqual(loaded.size, 13)
        self.assertEqual(loaded.color, "#ff0000")
        self.assertTrue(loaded.enabled)

    def test_save_writes_values_and_flushes_when_available(self):
        fake_modules = build_fake_environment(with_save_parameter=True)
        config, _ = import_runtime_modules(fake_modules)
        freecad_module = fake_modules["FreeCAD"]

        config.FontConfig(
            family="DejaVu Sans",
            size=12,
            color="#abcdef",
            enabled=True,
        ).save()

        self.assertEqual(
            fake_modules["store"],
            {
                "FontFamily": "DejaVu Sans",
                "FontSize": 12,
                "FontColor": "#abcdef",
                "Enabled": True,
            },
        )
        freecad_module.SaveParameter.assert_called_once_with()

    def test_save_skips_flush_when_unavailable(self):
        fake_modules = build_fake_environment(with_save_parameter=False)
        config, _ = import_runtime_modules(fake_modules)

        config.FontConfig(family="Ubuntu", size=11, color="", enabled=False).save()

        self.assertEqual(fake_modules["store"]["FontFamily"], "Ubuntu")
        self.assertNotIn("SaveParameter", vars(fake_modules["FreeCAD"]))


class TestCore(unittest.TestCase):
    def test_resolve_font_family_falls_back_to_application_font(self):
        fake_modules = build_fake_environment(
            families=["DejaVu Sans", "Liberation Sans"],
            app_family="DejaVu Sans",
        )
        _, core = import_runtime_modules(fake_modules)

        resolved, used_fallback = core.resolve_font_family("Segoe UI")

        self.assertEqual(resolved, "DejaVu Sans")
        self.assertTrue(used_fallback)

    def test_apply_uses_resolved_fallback_font(self):
        fake_modules = build_fake_environment(
            families=["DejaVu Sans", "Liberation Sans"],
            app_family="DejaVu Sans",
        )
        _, core = import_runtime_modules(fake_modules)

        result = core.apply("Segoe UI", 12, "#ff0000")

        self.assertTrue(result)
        self.assertIn('font-family: "DejaVu Sans";', fake_modules["window"].styleSheet())
        fake_modules["console"].PrintWarning.assert_called_once()
        fake_modules["console"].PrintMessage.assert_called_once()

    def test_apply_saved_applies_enabled_config(self):
        fake_modules = build_fake_environment(
            store={
                "FontFamily": "Ubuntu",
                "FontSize": 14,
                "FontColor": "#123456",
                "Enabled": True,
            },
            families=["Ubuntu", "DejaVu Sans"],
            app_family="Ubuntu",
        )
        _, core = import_runtime_modules(fake_modules)

        core.apply_saved()

        self.assertIn('font-family: "Ubuntu";', fake_modules["window"].styleSheet())
        self.assertIn("14pt", fake_modules["window"].styleSheet())
        self.assertIn("#123456", fake_modules["window"].styleSheet())

    def test_remove_drops_existing_fontbook_block(self):
        fake_modules = build_fake_environment(
            families=["Ubuntu"],
            app_family="Ubuntu",
            stylesheet='QWidget { background: #111; }\n/* FontBook:start */\n'
            'QWidget { font-family: "Ubuntu"; }\n/* FontBook:end */\n',
        )
        _, core = import_runtime_modules(fake_modules)

        core.remove()

        self.assertEqual(fake_modules["window"].styleSheet(), "QWidget { background: #111; }")

    def test_install_startup_hooks_schedules_reapply_once(self):
        fake_modules = build_fake_environment(families=["Ubuntu"], app_family="Ubuntu")
        _, core = import_runtime_modules(fake_modules)

        core.install_startup_hooks()
        core.install_startup_hooks()

        self.assertEqual(
            [delay for delay, _callback in FakeQTimer.calls],
            list(core.STARTUP_REAPPLY_DELAYS_MS),
        )


if __name__ == "__main__":
    unittest.main()
