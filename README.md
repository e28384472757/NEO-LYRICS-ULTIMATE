# NEO-LYRICS ULTIMATE

**SHADOW EMPEROR · Dual Mode · v1.2.0**

Letras sincronizadas de Spotify Desktop con una interfaz gráfica gótica HD (PySide6) y un modo terminal (Rich). El motor de letras LRCLIB y el sincronizador son compartidos.

> Estado: versión multiplataforma en preparación. Linux usa MPRIS/Playerctl; Windows usa Windows Global System Media Transport Controls (GSMTC). La integración GSMTC depende de Windows y del paquete opcional `winsdk`. La compatibilidad debe validarse en una sesión real de cada sistema.

## Plataformas

| Plataforma | GUI | Terminal | Detección Spotify |
|---|---:|---:|---|
| Arch / Manjaro / EndeavourOS | Sí | Sí | MPRIS + `playerctl` |
| Ubuntu / Debian / Mint | Sí | Sí | MPRIS + `playerctl` |
| Fedora | Sí | Sí | MPRIS + `playerctl` |
| openSUSE | Sí | Sí | MPRIS + `playerctl` |
| Otras distribuciones Linux | Sí | Sí | MPRIS + `playerctl` si está disponible |
| Windows 10/11 | Sí | Sí | Windows GSMTC + `winsdk` |

Python 3.10 o posterior y Spotify Desktop son necesarios. La GUI requiere PySide6. En Linux, `playerctl` es necesario para leer MPRIS; `chafa` es opcional para imágenes en terminal. En Windows, GSMTC solo funciona cuando Spotify publica su sesión de medios al sistema.

## Instalación Linux (todas las distribuciones)

```bash
chmod +x install.sh
./install.sh
```

El instalador crea un entorno virtual aislado en `~/.local/share/neolyrics-ultimate` y el comando en `~/.local/bin/neolyrics`. No utiliza `sudo`, no asume `pacman` y no instala paquetes del sistema. Instala `playerctl` y `chafa` desde el gestor de paquetes de tu distribución si quieres integración MPRIS e imagen terminal.

Si `~/.local/bin` no está en PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Instalación Windows 10/11

1. Instala Python 3.10+ desde https://www.python.org/downloads/ y activa **Add Python to PATH**.
2. Extrae el proyecto.
3. Abre PowerShell en la carpeta extraída:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1
```

Abre una nueva PowerShell. Ejecuta `neolyrics.cmd` desde `%LOCALAPPDATA%\NEO-LYRICS-ULTIMATE\bin` o añade esa carpeta al PATH si no se añadió automáticamente.

## Uso

```bash
neolyrics                 # GUI HD
neolyrics --gui            # GUI explícita
neolyrics --terminal       # Terminal Rich; Chafa opcional
neolyrics --help
neolyrics --version
```

En Windows el ejecutable generado es `neolyrics.exe` dentro del entorno virtual; el instalador añade un lanzador `neolyrics.cmd`.

## Desinstalación

Linux:

```bash
./uninstall.sh
```

Windows (PowerShell desde la carpeta del proyecto):

```powershell
.\uninstall.ps1
```

## Desarrollo

```bash
python -m venv .venv
# Linux: source .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1
python -m pip install -e ".[gui,dev]"
# Windows añade GSMTC: python -m pip install -e ".[gui,windows,dev]"
python -m pytest -q
python -m compileall -q neolyrics
```

## CI y releases

GitHub Actions ejecuta pruebas en Ubuntu y Windows. Las versiones se publican creando un tag `v*`; el workflow de release construye el paquete Python. Consulta `.github/workflows/`.

## Arquitectura

```text
neolyrics/
  core/       Spotify adapters, LRCLIB, parser LRC, sincronizador y motor
  gui/        PySide6
  terminal/   Rich + Chafa opcional
  cli.py      comando neolyrics
assets/       ilustración anime gótica
config/       configuración de referencia
tests/        pruebas unitarias
install.sh    instalador Linux genérico
install.ps1   instalador Windows
uninstall.*   desinstaladores
```

## Privacidad y seguridad

La aplicación no pide contraseñas de Spotify ni modifica la cuenta. En Linux lee metadatos locales MPRIS. En Windows lee la sesión de medios del sistema mediante GSMTC. Para buscar letras envía título, artista y álbum a LRCLIB. No intercepta tráfico ni modifica el cliente Spotify.

## Limitaciones

- LRCLIB no garantiza letras para todas las canciones.
- La integración Linux requiere que Spotify exponga una sesión MPRIS y que `playerctl` esté instalado.
- La integración Windows requiere que Spotify Desktop exponga GSMTC y que `winsdk` sea compatible con la versión de Python/Windows instalada.
- Chafa solo está disponible si el usuario lo instala; el modo terminal mantiene la interfaz Rich sin él.
- Las imágenes de portada pueden no estar disponibles según el proveedor de metadatos.
- El ecualizador de la interfaz es una animación visual, no un análisis de señal de audio.

## Contribuir

Pull requests, reportes de errores y pruebas en distribuciones adicionales son bienvenidos. Incluye sistema operativo, versión de Python, versión de Spotify y logs sin datos personales.
