#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${NEOLYRICS_INSTALL_DIR:-$HOME/.local/share/neolyrics-ultimate}"
BIN_DIR="${NEOLYRICS_BIN_DIR:-$HOME/.local/bin}"
PYTHON="${PYTHON:-python3}"
command -v "$PYTHON" >/dev/null || { echo "Python 3.10+ no encontrado." >&2; exit 1; }
"$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' || { echo "Se requiere Python 3.10 o posterior." >&2; exit 1; }
mkdir -p "$APP_DIR" "$BIN_DIR"
cp -a "$ROOT"/. "$APP_DIR"/
"$PYTHON" -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
"$APP_DIR/.venv/bin/python" -m pip install "$APP_DIR[gui]"
cat > "$BIN_DIR/neolyrics" <<EOF
#!/usr/bin/env sh
exec "$APP_DIR/.venv/bin/neolyrics" "\$@"
EOF
chmod 755 "$BIN_DIR/neolyrics"
if command -v playerctl >/dev/null; then echo "playerctl disponible."; else echo "Aviso: instala playerctl desde el gestor de paquetes de tu distribución para Spotify en Linux."; fi
if command -v chafa >/dev/null; then echo "Chafa disponible para gráficos de terminal."; else echo "Aviso: Chafa es opcional; el modo terminal seguirá funcionando sin imagen."; fi
case ":$PATH:" in *":$BIN_DIR:"*) ;; *) echo "Añade $BIN_DIR a PATH (por ejemplo: export PATH=\"\$HOME/.local/bin:\$PATH\").";; esac
echo "Instalado. Ejecuta: $BIN_DIR/neolyrics"
