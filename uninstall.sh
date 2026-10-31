#!/usr/bin/env bash
set -euo pipefail
APP_DIR="${NEOLYRICS_INSTALL_DIR:-$HOME/.local/share/neolyrics-ultimate}"
BIN_DIR="${NEOLYRICS_BIN_DIR:-$HOME/.local/bin}"
rm -rf -- "$APP_DIR"
rm -f -- "$BIN_DIR/neolyrics"
echo "NEO-LYRICS ULTIMATE desinstalado (dependencias Python aisladas eliminadas)."
