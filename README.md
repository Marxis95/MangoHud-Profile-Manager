A lightweight, Python-based GUI for managing MangoHud profiles. This tool allows you to easily toggle and configure your performance overlay settings on Linux.

## 🚀 Features
* **Profile Management:** Quickly switch between different MangoHud configurations.
* **Process Monitor:** Uses `psutil` to monitor system resources.
* **Desktop Integration:** Includes scripts for easy installation and menu integration.

---

## 📦 Installation

### 1. AppImage (Recommended)
The easiest way to run MangoManager is via the AppImage.
1. Download the latest `.AppImage` from the [Releases](https://github.com/Marxis95/MangoHud-Profile-Manager/releases) tab.
2. Navigate to the `Appimage` folder in this repo.
3. Run the installer script to integrate it into your system menu:
   ```bash
   chmod +x install.sh
   ./install.sh

### 2. Flatpak build from source (NOT Recommended)

If you prefer Flatpak, you can build it using the provided manifest:
Bash

flatpak-builder --user --install --force-clean build-dir flatpak/io.github.Marxis95.MangoManager.yml

🛠 Running from Source

If you want to run the code directly or contribute to development:
Prerequisites

    Python 3.12+

    pip


🗑 Uninstallation

To remove the AppImage and desktop shortcuts:
Bash

cd Appimage
chmod +x uninstall.sh
./uninstall.sh

To remove the flatpak:
flatpak uninstall io.github.Marxis95.MangoHud_Profile_Manager
