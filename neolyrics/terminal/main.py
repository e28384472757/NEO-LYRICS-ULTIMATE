"""High-resolution Konsole frontend using Chafa pixel protocols + Rich.

On capable terminals Chafa emits a real bitmap (SIXEL/Kitty/iTerm2), not a
character mosaic. Unsupported terminals receive a 24-bit sextant fallback.
The Spotify/LRCLIB state is provided by the same LyricsEngine as the GUI.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.text import Text

from neolyrics.core.animation import format_time, progress_fraction
from neolyrics.core.engine import EngineState, LyricsEngine

console = Console(highlight=False, soft_wrap=True)


def _asset_path() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "anime_background.png"


def _terminal_dimensions() -> tuple[int, int]:
    size = shutil.get_terminal_size((100, 32))
    return max(40, size.columns), max(20, size.lines)


def _graphics_protocol(payload: bytes) -> str:
    if b"\x1bP" in payload or b"\x90" in payload:
        return "SIXEL / PIXEL GRAPHICS"
    if b"\x1b_G" in payload:
        return "KITTY PIXEL GRAPHICS"
    if b"\x1b]1337;" in payload:
        return "ITERM2 PIXEL GRAPHICS"
    return "TRUECOLOR / SEXTANT FALLBACK"


def show_high_resolution_art() -> str:
    """Draw the bundled artwork once, above the live Rich playback panel.

    Chafa probes the active terminal. Konsole supports SIXEL, so on Konsole
    the PNG is sent as bitmap graphics and remains pixel-based. If the
    terminal lacks a bitmap protocol, Chafa falls back to truecolor symbols.
    """
    art = _asset_path()
    if not art.is_file():
        return "ARTWORK NOT FOUND"
    chafa = shutil.which("chafa")
    if not chafa or not console.is_terminal:
        return "TEXT MODE · CHAFa UNAVAILABLE"

    width, height = _terminal_dimensions()
    art_rows = max(5, min(17, height - 19))
    art_cols = max(32, min(width - 4, 100))
    mode = os.environ.get("NEOLYRICS_TERMINAL_IMAGE_MODE", "auto").strip().lower()

    command = [
        chafa,
        "--probe", "0.35",
        "--probe-mode", "ctty",
        "--colors", "full",
        "--size", f"{art_cols}x{art_rows}",
        "--view-size", f"{art_cols}x{art_rows}",
        "--align", "center",
        "--relative", "off",
        "--margin-bottom", "0",
        "--optimize", "8",
        "--dither", "diffusion",
        "--symbols", "sextant",
        "--font-ratio", "1/2",
    ]
    if mode in {"pixel", "sixel", "sixels", "hd"}:
        command.extend(["--format", "sixels"])
    elif mode in {"symbols", "text", "ansi"}:
        command.extend(["--format", "symbols"])
    command.append(str(art))

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=4,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "ARTWORK FALLBACK"

    if result.returncode != 0 or not result.stdout:
        return "ARTWORK FALLBACK"

    # Bypass Rich's text sanitizer: graphics protocols are binary terminal
    # control sequences and must reach Konsole unchanged.
    raw_stream = getattr(console.file, "buffer", None)
    if raw_stream is not None:
        raw_stream.write(result.stdout)
        raw_stream.flush()
    else:
        console.file.write(result.stdout.decode("utf-8", errors="replace"))
        console.file.flush()
    console.file.write("\n")
    console.file.flush()
    return _graphics_protocol(result.stdout)


def _spectrum(phase: int, width: int) -> Text:
    levels = "▁▂▃▄▅▆▇█"
    count = max(18, min(54, width - 18))
    values = []
    for i in range(count):
        level = (i * 3 + phase * (i % 5 + 1) + (i * i // 7)) % len(levels)
        values.append(levels[level])
    out = Text("  ".join(values), style="bold bright_magenta")
    out.justify = "center"
    return out


def render(state: EngineState, phase: int = 0) -> Panel:
    width, _ = _terminal_dimensions()
    track = state.track

    title = Text(track.title if track else "Esperando a Spotify…", style="bold white")
    artist = Text(track.artist if track else "Abre Spotify y reproduce una canción", style="bright_magenta")
    if track and track.album:
        album = Text(track.album, style="dim bright_blue")
    else:
        album = Text("NEO-LYRICS · SHADOW EMPEROR", style="dim bright_blue")

    if state.lyrics_loading:
        lyric = Text("Buscando letras sincronizadas…", style="bold yellow")
    elif not track:
        lyric = Text("✦  La música comienza cuando tú presionas play  ✦", style="bold bright_cyan")
    elif not state.lyrics:
        lyric = Text(state.message or "No hay letras sincronizadas disponibles.", style="yellow")
    elif state.frame and state.frame.index < 0:
        lyric = Text("✧  La canción está por comenzar  ✧", style="bold bright_blue")
    else:
        lyric = Text(state.frame.visible if state.frame else "", style="bold white")
        if not lyric.plain:
            lyric = Text("·", style="bold bright_magenta")
    lyric.justify = "center"

    status_color = "green" if state.status == "Playing" else "yellow"
    connection = Text()
    connection.append("●  ", style=status_color if state.connected else "red")
    connection.append(
        "SPOTIFY CONECTADO" if state.connected else "SPOTIFY DESCONECTADO",
        style="bold " + ("green" if state.connected else "red"),
    )
    connection.append("   ·   ", style="dim")
    connection.append(state.status.upper(), style="bold bright_cyan")
    if track:
        connection.append(
            f"   ·   {format_time(state.position)} / {format_time(track.duration)}",
            style="bright_blue",
        )

    bar_width = max(20, min(56, width - 36))
    bar = ProgressBar(
        total=100,
        completed=progress_fraction(state.position, track.duration) * 100 if track else 0,
        width=bar_width,
        complete_style="bright_magenta",
        finished_style="bright_magenta",
        pulse_style="bright_blue",
    )

    content = Group(
        Align.center(title),
        Align.center(artist),
        Align.center(album),
        Text(""),
        Align.center(Text("✦  SHADOW SYNC  ✦", style="bold bright_magenta")),
        Align.center(lyric),
        Text(""),
        Align.center(connection),
        Align.center(bar),
        Align.center(_spectrum(phase, width)),
        Align.center(Text("LRCLIB  ·  MPRIS / PLAYERCTL  ·  TYPEWRITER SYNC", style="dim bright_blue")),
        Align.center(Text("CTRL+C  ·  SALIR", style="dim")),
    )
    return Panel(
        content,
        border_style="bright_magenta",
        title="[bold bright_blue]✦ NEO-LYRICS ULTIMATE ✦[/]",
        subtitle="[dim]SHADOW EMPEROR  /  LIVE LYRICS[/]",
        padding=(0, 2),
    )


def main() -> None:
    if not console.is_terminal:
        console.print("El modo terminal está diseñado para Konsole o una terminal interactiva.")

    console.clear(home=True)
    console.print(Align.center(Text("✦  N E O  —  L Y R I C S  U L T I M A T E  ✦", style="bold bright_magenta")))
    console.print(Align.center(Text("PIXEL ART  ·  SPOTIFY  ·  SYNCHRONIZED LYRICS", style="bright_blue")))
    graphics_mode = show_high_resolution_art()
    console.print(Align.center(Text(f"◈  {graphics_mode}  ◈", style="dim bright_cyan")))

    engine = LyricsEngine()
    try:
        phase = 0
        with Live(
            render(engine.snapshot()),
            console=console,
            screen=False,
            transient=False,
            refresh_per_second=12,
            vertical_overflow="crop",
        ) as live:
            while True:
                phase += 1
                live.update(render(engine.tick(), phase), refresh=True)
                time.sleep(0.25)
    except KeyboardInterrupt:
        console.print("\n[bold bright_magenta]✦ NEO-LYRICS desconectado. Hasta la próxima. ✦[/]")
    finally:
        engine.close()


if __name__ == "__main__":
    main()
