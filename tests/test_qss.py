import os
import sys
import unittest

# Ensure the addon root is in path so 'fontbook' can be imported natively 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fontbook import qss


class TestQSS(unittest.TestCase):
    def test_build_qss_uses_curated_color_targets(self):
        """Global color overrides should cover the expected UI chrome."""
        result = qss.build_qss("Ubuntu", 12, "#ff0000")
        self.assertIn("Ubuntu", result)
        self.assertIn("12pt", result)
        self.assertIn(qss.COLOR_TARGETS, result)
        self.assertIn("QLabel", result)
        self.assertIn("QGroupBox::title", result)
        self.assertIn("QMenuBar::item", result)
        self.assertIn("QMenu::item", result)
        self.assertIn("QTabBar::tab", result)
        self.assertIn("Gui--WorkbenchComboBox", result)
        self.assertNotIn("QAbstractButton", result)

    def test_build_qss_does_not_target_special_views(self):
        """Only targeted FreeCAD panels should be colored, not generic views."""
        result = qss.build_qss("Ubuntu", 12, "#ff0000")
        self.assertNotIn("QTextEdit", result)
        self.assertNotIn("QPlainTextEdit", result)
        self.assertNotIn("\nQTreeView {", result)
        self.assertNotIn("\nQTreeView::item {", result)
        self.assertNotIn("\nQListView {", result)
        self.assertNotIn("\nQListView::item {", result)
        self.assertNotIn("QTableView", result)
        self.assertNotIn("QPushButton", result)

    def test_build_qss_keeps_preferences_dialog_readable(self):
        """Preferences widgets should receive the chosen color explicitly."""
        result = qss.build_qss("Ubuntu", 12, "#ff0000")
        self.assertIn(qss.PREFERENCES_TEXT_TARGETS, result)
        self.assertIn(f"{qss.PREFERENCES_TEXT_TARGETS} {{ color: #ff0000; }}", result)

    def test_build_qss_targets_tree_and_property_panels_explicitly(self):
        """Tree and property panels should be colored via targeted selectors."""
        result = qss.build_qss("Ubuntu", 12, "#ff0000")
        self.assertIn(qss.COLOR_DIALOG_TEXT_TARGETS, result)
        self.assertIn(qss.WORKBENCH_POPUP_TARGETS, result)
        self.assertIn(qss.TREE_PANEL_TEXT_TARGETS, result)
        self.assertIn(qss.PROPERTY_EDITOR_ROOT_TARGETS, result)
        self.assertIn(qss.PROPERTY_EDITOR_LEFT_ITEM_TARGETS, result)
        self.assertIn(qss.PROPERTY_EDITOR_VALUE_TARGETS, result)
        self.assertIn(qss.PROPERTY_EDITOR_OVERLAY_VALUE_TARGETS, result)
        self.assertIn("qproperty-groupTextColor: #ff0000", result)
        self.assertIn("color: #ff0000", result)
        self.assertIn("palette(windowText)", result)
        self.assertIn("palette(text)", result)
        self.assertIn("palette(base)", result)

    def test_split_qss_no_ghosts(self):
        """Ensure multiple ghost blocks are fully removed (idempotency)."""
        block1 = qss.build_qss("Arial", 10, "")
        block2 = qss.build_qss("Ubuntu", 12, "#ffffff")
        
        simulated_sheet = f"QWidget {{ background: #000; }}{block1}QMenu {{ padding: 2px; }}{block2}"

        base_sheet, current_block = qss.split_qss(simulated_sheet)

        self.assertNotIn(qss.QSS_TAG, base_sheet)
        self.assertEqual(base_sheet, "QWidget { background: #000; }QMenu { padding: 2px; }")

    def test_split_qss_extracts_first_match_as_current(self):
        """If there are multiple blocks, match.group(0) extracts the first one."""
        block1 = qss.build_qss("Arial", 10, "")
        block2 = qss.build_qss("Ubuntu", 12, "#ffffff")
        simulated_sheet = f"QWidget {{ background: #000; }}{block1}QMenu {{ padding: 2px; }}{block2}"
        
        _, current_block = qss.split_qss(simulated_sheet)
        self.assertEqual(current_block.strip(), block1.strip())

    def test_split_qss_removes_legacy_blocks(self):
        """Legacy FontBook tags should still be removed during cleanup."""
        legacy_block = (
            '\n/* FontBook */\n'
            'QWidget { font-family: "Arial"; font-size: 10pt; }\n'
            "/* FontBook */\n"
        )
        base_sheet, current_block = qss.split_qss(
            f"QWidget {{ background: #000; }}{legacy_block}QMenu {{ padding: 2px; }}"
        )

        self.assertEqual(base_sheet, "QWidget { background: #000; }QMenu { padding: 2px; }")
        self.assertEqual(current_block.strip(), legacy_block.strip())

    def test_split_qss_strips_orphan_block_to_avoid_ghosts(self):
        """Broken trailing FontBook blocks should be discarded safely."""
        broken_sheet = (
            "QWidget { background: #000; }\n"
            "/* FontBook:start */\n"
            'QWidget { font-family: "Arial"; font-size: 10pt; }\n'
        )

        base_sheet, current_block = qss.split_qss(broken_sheet)

        self.assertEqual(base_sheet, "QWidget { background: #000; }")
        self.assertEqual(current_block, "")

if __name__ == '__main__':
    unittest.main()
