#!/bin/bash

APP_NAME="MangoHud Profile Manager"
FILE_ID="mangomanager"

INSTALL_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons"
DESKTOP_DIR="$HOME/.local/share/applications"

# 1. Ask for confirmation
zenity --question \
       --title="Uninstall $APP_NAME" \
       --text="Are you sure you want to remove $APP_NAME and all its associated files?" \
       --width=300 || exit

# 2. Remove the AppImage
if [ -f "$INSTALL_DIR/$FILE_ID.AppImage" ]; then
    rm "$INSTALL_DIR/$FILE_ID.AppImage"
fi

# 3. Remove the Desktop Entry
if [ -f "$DESKTOP_DIR/$FILE_ID.desktop" ]; then
    rm "$DESKTOP_DIR/$FILE_ID.desktop"
fi

# 4. Remove the Icon
if [ -f "$ICON_DIR/$FILE_ID.png" ]; then
    rm "$ICON_DIR/$FILE_ID.png"
fi

# 5. Update the desktop database to refresh the menu
update-desktop-database "$DESKTOP_DIR" 2>/dev/null

# 6. Success message
zenity --info \
       --title="Uninstall Complete" \
       --text="$APP_NAME has been successfully removed from your system." \
       --width=300
