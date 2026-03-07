#!/bin/bash
APP_NAME="MangoHud Profile Manager"
FILE_ID="mangomanager"

INSTALL_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons"
DESKTOP_DIR="$HOME/.local/share/applications"
APPIMAGE_FILE="MangoManager-x86_64.AppImage"

# 1. Ask for confirmation
zenity --question --text="Do you want to install $APP_NAME?" --title="Install $APP_NAME" || exit

# 2. Check if AppImage exists
if [ ! -f "$APPIMAGE_FILE" ]; then
    zenity --error --text="Error: $APPIMAGE_FILE not found in this folder."
    exit
fi

# 3. Create directories
mkdir -p "$INSTALL_DIR" "$ICON_DIR" "$DESKTOP_DIR"

# 4. Copy the AppImage
cp "$APPIMAGE_FILE" "$INSTALL_DIR/$FILE_ID.AppImage"
chmod +x "$INSTALL_DIR/$FILE_ID.AppImage"

# 5. Icon Detection Logic
# Check for 'mangomanager.png' OR 'icon.png'
if [ -f "mangomanager.png" ]; then
    cp "mangomanager.png" "$ICON_DIR/$FILE_ID.png"
    FINAL_ICON="$ICON_DIR/$FILE_ID.png"
elif [ -f "icon.png" ]; then
    cp "icon.png" "$ICON_DIR/$FILE_ID.png"
    FINAL_ICON="$ICON_DIR/$FILE_ID.png"
else
    # Fallback to a system icon if no PNG is provided in the folder
    FINAL_ICON="utilities-system-monitor"
fi

# 6. Create the Desktop Entry
cat <<EOF > "$DESKTOP_DIR/$FILE_ID.desktop"
[Desktop Entry]
Type=Application
Name=$APP_NAME
Comment=Manage MangoHud Profiles
Exec=$INSTALL_DIR/$FILE_ID.AppImage
Icon=$FINAL_ICON
Terminal=false
Categories=Game;Utility;
EOF

# Update the desktop database so the icon shows up immediately
update-desktop-database "$DESKTOP_DIR" 2>/dev/null

zenity --info --text="$APP_NAME installed successfully! Check your app menu." --title="Success"
