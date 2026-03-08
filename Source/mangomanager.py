import sys
import os
import psutil
import subprocess
import shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QSplitter,
                               QListWidget, QWidget, QVBoxLayout, QMenu, QLineEdit,
                               QCheckBox, QLabel, QScrollArea, QPushButton,
                               QComboBox, QHBoxLayout, QMessageBox, QDialog,
                               QFormLayout, QInputDialog) # FIXED: Removed underscore
from PySide6.QtCore import Qt, QTimer

VSYNC_MAP = {
    "Unset": "-1",
    "Adaptive": "0",
    "Off": "1",
    "Mailbox": "2",
    "On": "3"
}

class GameSelectionDialog(QDialog):
    def __init__(self, games, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Games Detected")
        self.setMinimumWidth(350)
        self.setMinimumHeight(400)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Select a game to create a profile for:</b>"))

        self.list_widget = QListWidget()
        self.list_widget.addItems(games)
        self.list_widget.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.list_widget)

        self.select_btn = QPushButton("Create Profile")
        self.select_btn.setStyleSheet("height: 30px; font-weight: bold;")
        self.select_btn.clicked.connect(self.accept)
        layout.addWidget(self.select_btn)

    def get_selection(self):
        if self.list_widget.currentItem():
            return self.list_widget.currentItem().text()
        return None

class MangoManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MangoHud Profile Manager")
        self.resize(1000, 650)

        # --- UNIVERSAL PATH DISCOVERY ---
        flatpak_path = os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.config/MangoHud/")
        standard_path = os.path.expanduser("~/.config/MangoHud/")

        if os.path.exists(flatpak_path):
            self.config_dir = flatpak_path
            self.is_flatpak = True
        else:
            self.config_dir = standard_path
            self.is_flatpak = False
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)

        self.QUICK_TWEAKS = [
            ("fps_limit", "FPS Limit (0, 60, 144)", "input"),
            ("fps_limit_method", "Limit Method", ["early", "late"]),
            ("vsync", "VSync Mode", list(VSYNC_MAP.keys())),
        ]

        self.option_widgets = {}
        self.init_ui()
        self.refresh_profiles()

    def init_ui(self):
        self.splitter = QSplitter(Qt.Horizontal)

        # --- LEFT SIDE: SIDEBAR ---
        self.sidebar = QWidget()
        self.side_layout = QVBoxLayout(self.sidebar)

        search_row = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search profiles...")
        self.search_bar.textChanged.connect(self.filter_profiles)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedWidth(35)
        self.refresh_btn.clicked.connect(self.refresh_profiles)

        search_row.addWidget(self.search_bar)
        search_row.addWidget(self.refresh_btn)

        self.profile_list = QListWidget()
        self.profile_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.profile_list.customContextMenuRequested.connect(self.show_context_menu)
        self.profile_list.itemClicked.connect(self.load_selected_profile)

        self.side_layout.addWidget(QLabel("<b>Profiles</b>"))
        self.side_layout.addLayout(search_row)
        self.side_layout.addWidget(self.profile_list)

        self.side_layout.addSpacing(10)
        self.side_layout.addWidget(QLabel("<b>Steam Launch Argument:</b>"))

        default_arg = "MANGOHUD=1 %command%" if self.is_flatpak else "mangohud %command%"
        self.launch_cmd = QLineEdit(default_arg)
        self.launch_cmd.setReadOnly(True)
        self.launch_cmd.setStyleSheet("""
            QLineEdit { background-color: #e0e0e0; color: #222222; padding: 5px; border: 1px solid #bbb; font-family: monospace; }
        """)

        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)

        self.side_layout.addWidget(self.launch_cmd)
        self.side_layout.addWidget(self.copy_btn)

        if self.is_flatpak:
            self.fix_btn = QPushButton("🛠 Fix Flatpak Permissions")
            self.fix_btn.setStyleSheet("background-color: #5c6bc0; color: white;")
            self.fix_btn.clicked.connect(self.fix_flatpak_permissions)
            self.side_layout.addWidget(self.fix_btn)

        self.scan_btn = QPushButton("🔍 Scan for Running Games")
        self.scan_btn.setStyleSheet("background-color: #2e7d32; color: white; height: 35px; font-weight: bold; margin-top: 10px;")
        self.scan_btn.clicked.connect(self.scan_for_games)
        self.side_layout.addWidget(self.scan_btn)

        self.splitter.addWidget(self.sidebar)

        # --- RIGHT SIDE: QUICK TWEAKS ---
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.form_layout = QFormLayout()

        header = QLabel("Performance Settings")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #444; margin-bottom: 10px;")
        self.right_layout.addWidget(header)

        for key, label, ui_type in self.QUICK_TWEAKS:
            if ui_type == "toggle":
                w = QCheckBox()
                w.toggled.connect(self.save_config)
            elif isinstance(ui_type, list):
                w = QComboBox()
                w.addItems(ui_type)
                w.currentTextChanged.connect(self.save_config)
            else:
                w = QLineEdit()
                w.textChanged.connect(self.save_config)

            self.form_layout.addRow(label, w)
            self.option_widgets[key] = w


        self.right_layout.addLayout(self.form_layout)
        self.right_layout.addStretch()
        self.right_layout.addWidget(QLabel("<i>Note: Other settings are preserved when editing.</i>"))
        self.open_folder_btn = QPushButton("📂 Open Config Folder")
        self.open_folder_btn.setStyleSheet("height: 30px; margin-bottom: 10px;")
        self.open_folder_btn.clicked.connect(lambda: self.safe_open(self.config_dir))
        self.right_layout.addWidget(self.open_folder_btn)
        self.form_layout = QFormLayout()
        self.splitter.addWidget(self.right_panel)
        self.setCentralWidget(self.splitter)

    # --- LOGIC ---

    def fix_flatpak_permissions(self):
        try:
            cmd = ["flatpak", "override", "--user", "--filesystem=xdg-config/MangoHud:ro", "com.valvesoftware.Steam"]
            subprocess.run(cmd, check=True)
            QMessageBox.information(self, "Success", "Permissions granted! Restart Steam for the changes to take effect.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not set permissions: {e}")

    def refresh_profiles(self):
        self.search_bar.clear()
        self.profile_list.clear()
        if os.path.exists(self.config_dir):
            files = [f for f in os.listdir(self.config_dir) if f.endswith('.conf')]
            self.profile_list.addItems(sorted(files))

    def load_selected_profile(self, item):
        path = os.path.join(self.config_dir, item.text())
        data = {}
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    if '=' in line:
                        k, v = line.split('=', 1)
                        data[k.strip()] = v.strip()
                    else:
                        data[line] = True
        except: pass

        for w in self.option_widgets.values(): w.blockSignals(True)
        for key, widget in self.option_widgets.items():
            if isinstance(widget, QCheckBox):
                widget.setChecked(key in data)
            elif isinstance(widget, QComboBox):
                raw_val = data.get(key, "")
                if key == "vsync":
                    display_name = next((k for k, v in VSYNC_MAP.items() if v == raw_val), "Unset")
                    index = widget.findText(display_name)
                else:
                    index = widget.findText(raw_val)
                widget.setCurrentIndex(index if index >= 0 else 0)
            else:
                widget.setText(data.get(key, ""))
        for w in self.option_widgets.values(): w.blockSignals(False)

    def save_config(self):
        item = self.profile_list.currentItem()
        if not item: return
        path = os.path.join(self.config_dir, item.text())

        existing_lines = []
        if os.path.exists(path):
            with open(path, 'r') as f: existing_lines = f.readlines()

        ui_updates = {}
        for key, widget in self.option_widgets.items():
            if isinstance(widget, QCheckBox): ui_updates[key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                val = widget.currentText()
                ui_updates[key] = VSYNC_MAP.get(val, "-1") if key == "vsync" else val
            else: ui_updates[key] = widget.text()

        new_lines = []
        handled_keys = set()
        for line in existing_lines:
            clean = line.strip()
            found_key = None
            for key in ui_updates.keys():
                if clean.startswith(f"{key}=") or clean == key:
                    found_key = key
                    break

            if found_key:
                handled_keys.add(found_key)
                val = ui_updates[found_key]
                if isinstance(val, bool):
                    if val: new_lines.append(f"{found_key}\n")
                elif val and val != "-1":
                    new_lines.append(f"{found_key}={val}\n")
            else:
                new_lines.append(line)

        for key, val in ui_updates.items():
            if key not in handled_keys:
                if isinstance(val, bool) and val: new_lines.append(f"{key}\n")
                elif isinstance(val, str) and val and val != "-1": new_lines.append(f"{key}={val}\n")

        with open(path, "w") as f: f.writelines(new_lines)

    def show_context_menu(self, pos):
        item = self.profile_list.itemAt(pos)
        if not item: return
        path = os.path.join(self.config_dir, item.text())
        menu = QMenu()
        menu.addAction("Edit", lambda: self.safe_open(path))
        menu.addSeparator()
        menu.addAction("Rename", lambda: self.prompt_rename(item))
        menu.addAction("Duplicate", lambda: self.duplicate_profile(item))
        menu.addSeparator()
        menu.addAction("Delete", lambda: [os.remove(path), self.refresh_profiles()])
        menu.exec(self.profile_list.mapToGlobal(pos))

    def prompt_rename(self, item):
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=item.text())
        if ok and new_name:
            if not new_name.endswith(".conf"): new_name += ".conf"
            os.rename(os.path.join(self.config_dir, item.text()), os.path.join(self.config_dir, new_name))
            self.refresh_profiles()

    def duplicate_profile(self, item):
        new_name = item.text().replace(".conf", "_copy.conf")
        shutil.copy2(os.path.join(self.config_dir, item.text()), os.path.join(self.config_dir, new_name))
        self.refresh_profiles()

    def filter_profiles(self, text):
        for i in range(self.profile_list.count()):
            it = self.profile_list.item(i)
            it.setHidden(text.lower() not in it.text().lower())

    def scan_for_games(self):
        discovered = []
        blacklist = ["steam", "explorer", "discord", "python", "systemd", "mangohud", "winedevice", "services", "svchost", "plugplay", "rpcss", "tabtip"]
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].endswith(".exe"):
                    clean = proc.info['name'].replace(".exe", "")
                    mh_name = f"wine-{clean}.conf"
                    if mh_name not in discovered and not any(b in clean.lower() for b in blacklist):
                        discovered.append(mh_name)
            except: continue

        if not discovered:
            QMessageBox.information(self, "Scanner", "No running games detected.")
            return

        dialog = GameSelectionDialog(discovered, self)
        if dialog.exec_():
            game = dialog.get_selection()
            if game:
                path = os.path.join(self.config_dir, game)
                global_conf_path = os.path.join(self.config_dir, "MangoHud.conf")
                if not os.path.exists(path):
                    if os.path.exists(global_conf_path):
                        try:
                            shutil.copy2(global_conf_path, path)
                            with open(path, 'r+') as f:
                                content = f.read()
                                f.seek(0, 0)
                                f.write(f"# Cloned from Global MangoHud.conf\n\n" + content)
                        except: pass
                    else:
                        with open(path, 'w') as f: f.write("# New Profile\n")

                self.refresh_profiles()
                items = self.profile_list.findItems(game, Qt.MatchExactly)
                if items:
                    self.profile_list.setCurrentItem(items[0])
                    self.load_selected_profile(items[0])

    def safe_open(self, path):
        # 1. Basic validation
        if not path or not os.path.exists(path):
            return

        # 2. Get environment
        clean_env = dict(os.environ)
        
        # 3. Detect if we are in an AppImage (The only place we need to fix things)
        # AppImages always set the 'APPIMAGE' environment variable.
        if 'APPIMAGE' in clean_env or 'APPDIR' in clean_env:
            keys_to_reset = ['LD_LIBRARY_PATH', 'PYTHONPATH', 'PYTHONHOME', 'LD_PRELOAD']
            for key in keys_to_reset:
                orig_key = f"{key}_ORIG"
                if orig_key in clean_env:
                    clean_env[key] = clean_env[orig_key]
                else:
                    clean_env.pop(key, None)
            
            # AppImage launch
            try:
                subprocess.Popen(['xdg-open', path], env=clean_env, start_new_session=True)
            except Exception as e:
                print(f"AppImage launch error: {e}")
        else:
            # Flatpak or Local: Just use the system default behavior.
            # Do NOT pass 'env=clean_env' here, let it inherit naturally.
            try:
                subprocess.Popen(['xdg-open', path])
            except Exception as e:
                print(f"Standard launch error: {e}")
              
    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.launch_cmd.text())
        orig = self.copy_btn.text()
        self.copy_btn.setText("✅ Copied!")
        QTimer.singleShot(1500, lambda: self.copy_btn.setText(orig))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MangoManager()
    win.show()
    sys.exit(app.exec())
