# FontChanger

<p align="center">
  <img src="resources/icons/fontchanger.svg" width="128" />
</p>

Change the FreeCAD UI font to any system-installed font.
Works on **all platforms** (Linux, Windows, macOS) and **all packaging formats** (AppImage, Flatpak, native).

## Installation

### Via Addon Manager
1. **Tools → Addon Manager** → search "FontChanger" → Install → Restart

### Manual
```bash
# Linux
cd ~/.local/share/FreeCAD/Mod/
git clone https://github.com/arcanorca/FontChanger.git

# Windows
# cd %APPDATA%\FreeCAD\Mod\
# git clone https://github.com/arcanorca/FontChanger.git

# macOS
# cd ~/Library/Application\ Support/FreeCAD/Mod/
# git clone https://github.com/arcanorca/FontChanger.git
```
Restart FreeCAD after installing.

## Usage
1. **Edit → Preferences → Display** → find the **FontChanger** tab
2. Enable, pick a font, set the size, click **OK**
3. The font changes immediately — no restart needed

Settings are saved to `user.cfg` and re-applied on every startup.
If a saved font is not available on the current OS, FontChanger falls back to
the active system UI font instead of failing silently.

## How It Works
FontChanger dynamically appends a tagged, in-memory stylesheet block (QSS) directly to FreeCAD's active main window stylesheet:
```css
/* FontChanger:start */
QWidget { font-family: "YourFont"; font-size: 11pt; }
QLabel, QAbstractButton, QListView, QTreeView { color: #CB333B; }
/* FontChanger:end */
```
No static theme files on your disk are modified. The injection is cleanly isolated using `/* FontChanger:start */` and `/* FontChanger:end */` tags, meaning the custom styles can be instantly updated, replaced, or completely removed on-the-fly via regular expressions. 

### Smart Color Overrides
When a custom text color is chosen, applying it blindly to `*` or `QWidget` would break the carefully curated semantic colors in data-heavy FreeCAD panels, such as syntax highlighting in the Python console or color-coded cells in Spreadsheet workbenches. 

Instead, FontChanger uses a strict **Allowlist System** to precisely override text colors *only* where it makes sense:
- General text elements (`QLabel`)
- All buttons (`QAbstractButton` subclasses including `QPushButton`, `QCheckBox`, `QRadioButton`)
- Structural dialog lists and trees (`QListView`, `QTreeView`) used in the Tasks Panel and UI sidebars.
- Data-heavy text inputs and views (like `QTextEdit`, `QTableView`) are explicitly excluded, safely falling back to the underlying FreeCAD theme's native semantic coloring.

This ensures seamless integration with dark or light themes while preserving maximum readability.

## License
[LGPL-2.1-or-later](LICENSE)

## Recent Updates
- **Improved Color Consistency**: Added robust support for styling checkboxes, radio buttons, and Task View lists globally across the FreeCAD interface.
- **Color Picker Fixes**: Streamlined the `QColorDialog` integration, completely replacing geometry-based custom-color removal with precise Qt-Layout parsing, fixing display bugs.
- **Brand Identity**: Updated `fontchanger.svg` with a polished, rounded geometry look featuring diverse typography styles!
