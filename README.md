# FontChanger

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
FontChanger appends a tagged stylesheet block to FreeCAD's active stylesheet:
```css
QWidget { font-family: "YourFont"; font-size: 11pt; }
```
No theme files are modified. The injection is tag-delimited so it can be cleanly replaced or removed.

## License
[LGPL-2.1-or-later](LICENSE)

## Recent Updates
- **Improved Color Consistency**: Added robust support for styling checkboxes, radio buttons, and Task View lists globally across the FreeCAD interface.
- **Color Picker Fixes**: Streamlined the `QColorDialog` integration, completely replacing geometry-based custom-color removal with precise Qt-Layout parsing, fixing display bugs.
- **Brand Identity**: Updated `fontchanger.svg` with a polished, rounded geometry look featuring diverse typography styles!
