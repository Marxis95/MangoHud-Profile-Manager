A lightweight, Python-based GUI for managing MangoHud profiles. This tool allows you to easily toggle and configure your performance overlay settings on Linux.

## 🚀 Features
* **Profile Management:** Quickly switch between different MangoHud configurations.
* **Process Monitor:** Uses `psutil` to monitor system resources.
* **Desktop Integration:** Includes scripts for easy installation and menu integration.

---

## 📦 Installation

### 1. AppImage (Recommended)
The easiest way to run MangoManager is via the AppImage.
1. Download the latest archive (.zip file) from the [Releases](https://github.com/Marxis95/MangoHud-Profile-Manager/releases) tab.
2. Extract the Appimage folder to a place of your choosing.
3. Run the .appimage file if you want it as a portable version (allowing the file to execute) or using installer script to integrate it into your system menu :
   Allow the file to execute either through Dolphin if on KDE (right click--properties--Permissions--check allow executing file as program) or open a terminal into the Appimage folder and type:
   chmod +x install.sh
   then ./install.sh

2. Flatpak

If you prefer Flatpak, you can build it using the provided manifest:
Bash

flatpak-builder --user --install --force-clean build-dir flatpak/io.github.Marxis95.MangoManager.yml

🛠 Running from Source

If you want to run the code directly or contribute to development:
Prerequisites

    Python 3.12+

    pip

Setup

    Clone the repository:
    Bash

    git clone [https://github.com/Marxis95/MangoHud-Profile-Manager.git](https://github.com/Marxis95/MangoHud-Profile-Manager.git)
    cd MangoManager

    Create and activate a virtual environment:
    Bash

    python3 -m venv venv
    source venv/bin/activate  # Or activate.fish for Fish shell

    Install dependencies:
    Bash

    pip install PySide6-Essentials psutil

    Run the app:
    Bash

    python3 Source/mangomanager.py

🗑 Uninstallation

To remove the AppImage and desktop shortcuts:
Bash

cd Appimage
chmod +x uninstall.sh
./uninstall.sh
