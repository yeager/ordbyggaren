# Ordbyggaren

Phonological training app - build words from sounds and letters.

![Screenshot](screenshots/screenshot.png)

## Features

Syllables, sounds→letters mapping, drag letters to correct position, adjustable difficulty (easy/medium/hard), TTS for pronunciation. Swedish word lists.

## Requirements

- Python 3.10+
- GTK4 / libadwaita
- PyGObject

## Installation

```bash
# Install dependencies (Fedora/RHEL)
sudo dnf install python3-gobject gtk4 libadwaita

# Install dependencies (Debian/Ubuntu)
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1

# Run from source
PYTHONPATH=src python3 -c "from ordbyggaren.main import main; main()"
```

## License

GPL-3.0-or-later

## Author

Daniel Nylander

## Links

- [GitHub](https://github.com/yeager/ordbyggaren)
- [Issues](https://github.com/yeager/ordbyggaren/issues)
- [Translations](https://app.transifex.com/danielnylander/ordbyggaren)
