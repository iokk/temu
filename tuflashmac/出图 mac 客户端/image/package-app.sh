#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="电商出图工作台"
PACKAGE_ROOT="$ROOT_DIR/.release"
STAGE_DIR="$PACKAGE_ROOT/${APP_NAME}"
ZIP_PATH="$PACKAGE_ROOT/${APP_NAME}-app-package.zip"

mkdir -p "$PACKAGE_ROOT"
rm -rf "$STAGE_DIR" "$ZIP_PATH"
mkdir -p "$STAGE_DIR/.streamlit"

copy_file() {
  local src="$1"
  local dst="$2"
  cp "$ROOT_DIR/$src" "$STAGE_DIR/$dst"
}

copy_file ".env.example" ".env.example"
copy_file "README.md" "README.md"
copy_file "NEW-MAC-SETUP.md" "NEW-MAC-SETUP.md"
copy_file "app.py" "app.py"
copy_file "requirements.txt" "requirements.txt"
copy_file "start-local.sh" "start-local.sh"
copy_file "start-mac.command" "start-mac.command"
copy_file "stop-local.sh" "stop-local.sh"
copy_file "heartbeat_launcher.py" "heartbeat_launcher.py"
copy_file "install-mac-login-launcher.sh" "install-mac-login-launcher.sh"
copy_file "uninstall-mac-login-launcher.sh" "uninstall-mac-login-launcher.sh"
copy_file "configure-update-remote.sh" "configure-update-remote.sh"
copy_file ".streamlit/config.toml" ".streamlit/config.toml"

chmod +x \
  "$STAGE_DIR/start-local.sh" \
  "$STAGE_DIR/start-mac.command" \
  "$STAGE_DIR/stop-local.sh" \
  "$STAGE_DIR/heartbeat_launcher.py" \
  "$STAGE_DIR/install-mac-login-launcher.sh" \
  "$STAGE_DIR/uninstall-mac-login-launcher.sh" \
  "$STAGE_DIR/configure-update-remote.sh"

cd "$PACKAGE_ROOT"
COPYFILE_DISABLE=1 zip -qry -X "$ZIP_PATH" "$APP_NAME"

echo "Created package:"
echo "$ZIP_PATH"
