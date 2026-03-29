# FontBook

<p align="center">
  <img src="resources/icons/fontbook.svg" width="128" />
</p>

Change the FreeCAD UI font to any system-installed font.
Works on **all platforms** (Linux, Windows, macOS) and **all packaging formats** (AppImage, Flatpak, native).

## Installation

### Via Addon Manager
1. **Tools → Addon Manager** → search "FontBook" → Install → Restart

### Manual
```bash
# Linux
cd ~/.local/share/FreeCAD/Mod/
git clone https://github.com/arcanorca/FontBook.git

# Windows
# cd %APPDATA%\FreeCAD\Mod\
# git clone https://github.com/arcanorca/FontBook.git

# macOS
# cd ~/Library/Application\ Support/FreeCAD/Mod/
# git clone https://github.com/arcanorca/FontBook.git
```
Restart FreeCAD after installing.

## Usage
1. **Edit → Preferences → Display** → find the **FontBook** tab
2. Enable, pick a font, set the size, click **OK**
3. The font changes immediately — no restart needed

Settings are saved to `user.cfg` and re-applied on every startup.
If a saved font is not available on the current OS, FontBook falls back to
the active system UI font instead of failing silently.

## How It Works
FontBook appends a stylesheet block (QSS) to FreeCAD's stylesheet:
```css
/* FontBook:start */
QWidget { font-family: "YourFont"; font-size: 11pt; }
QLabel, QAbstractButton, QListView, QTreeView { color: #CB333B; }
/* FontBook:end */
```
The injection is tag-delimited so it can be updated or removed via string processing. 

### Color Overrides
Applying global colors blindly to `*` or `QWidget` can mess up colors in the Python console or Spreadsheets. 

FontBook instead overrides text colors on a limited set of widgets:
- General text elements (`QLabel`)
- All buttons (`QAbstractButton` subclasses including `QPushButton`, `QCheckBox`, `QRadioButton`)
- Structural dialog lists and trees (`QListView`, `QTreeView`) used in the Tasks Panel and UI sidebars.
- Data-heavy text inputs and views (like `QTextEdit`, `QTableView`) are excluded.



## License
[LGPL-2.1-or-later](LICENSE)

## Recent Updates
- **Improved Color Consistency**: Added robust support for styling checkboxes, radio buttons, and Task View lists globally across the FreeCAD interface.
- **Color Picker Fixes**: Streamlined the `QColorDialog` integration, completely replacing geometry-based custom-color removal with precise Qt-Layout parsing, fixing display bugs.
- **Brand Identity**: Updated `fontbook.svg` with a polished, rounded geometry look featuring diverse typography styles!
