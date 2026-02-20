# Ordbyggaren

[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/yeager/ordbyggaren/releases)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Transifex](https://img.shields.io/badge/Transifex-Translate-green.svg)](https://www.transifex.com/danielnylander/ordbyggaren/)

Phonological training app — build words from sounds and letters — GTK4/Adwaita.

> **For:** Children with developmental language disorder (DLD), autism, or dyslexia. Phonological awareness training through interactive word building.

![Screenshot](screenshots/main.png)

## Features

- **Word building** — drag letters and sounds to form words
- **Phoneme support** — individual sound segments
- **Progressive difficulty** — from simple to complex words
- **Visual feedback** — immediate right/wrong indication
- **Word categories** — animals, food, objects
- **Dark/light theme** toggle

## Installation

### Debian/Ubuntu

```bash
echo "deb [signed-by=/usr/share/keyrings/yeager-keyring.gpg] https://yeager.github.io/debian-repo stable main" | sudo tee /etc/apt/sources.list.d/yeager.list
curl -fsSL https://yeager.github.io/debian-repo/yeager-keyring.gpg | sudo tee /usr/share/keyrings/yeager-keyring.gpg > /dev/null
sudo apt update && sudo apt install ordbyggaren
```

### Fedora/openSUSE

```bash
sudo dnf config-manager --add-repo https://yeager.github.io/rpm-repo/yeager.repo
sudo dnf install ordbyggaren
```

### From source

```bash
git clone https://github.com/yeager/ordbyggaren.git
cd ordbyggaren && pip install -e .
ordbyggaren
```

## Translation

Help translate on [Transifex](https://www.transifex.com/danielnylander/ordbyggaren/).

## License

GPL-3.0-or-later — see [LICENSE](LICENSE) for details.

## Author

**Daniel Nylander** — [danielnylander.se](https://danielnylander.se)
