#!/usr/bin/env python3
"""NEO-LYRICS: synchronized Spotify lyrics for an anime-inspired terminal."""
import bisect
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()
PLAYER = "spotify"
POLL_INTERVAL = 0.25
LRC_TIME = re.compile(r"\[(\d{1,2}):(\d{2})(?:[.:](\d{1,3}))?\]")


def playerctl(*args):
    try:
        result = subprocess.run(
            ["playerctl", "-p", PLAYER, *args],
            capture_output=True, text=True, timeout=2, check=True
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def get_track():
    raw = playerctl("metadata", "--format",
                    "{{ artist }}|||{{ title }}|||{{ album }}|||{{ mpris:length }}")
    parts = raw.split("|||")
    if len(parts) < 4 or not parts[1]:
        return None
    try:
        duration = int(parts[3]) / 1_000_000
    except ValueError:
        duration = 0
    return {
        "artist": parts[0],
        "title": parts[1],
        "album": parts[2],
        "duration": duration,
    }


def parse_lrc(source):
    lines = []
    for raw_line in source.splitlines():
        stamps = LRC_TIME.findall(raw_line)
        lyric = LRC_TIME.sub("", raw_line).strip()
        if not stamps or not lyric:
            continue
        for minute, second, fraction in stamps:
            # LRC fractions may be tenths, hundredths, or milliseconds.
            frac = float("0." + fraction) if fraction else 0.0
            timestamp = int(minute) * 60 + int(second) + frac
            lines.append((timestamp, lyric))
    lines.sort(key=lambda item: item[0])
    return lines


def request_json(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NEO-LYRICS/1.0 (terminal lyrics client)"}
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_lyrics(track):
    params = {
        "artist_name": track["artist"],
        "track_name": track["title"],
        "album_name": track["album"],
    }
    if track["duration"]:
        params["duration"] = str(round(track["duration"]))
    url = "https://lrclib.net/api/get?" + urllib.parse.urlencode(params)
    try:
        data = request_json(url)
        synced = data.get("syncedLyrics")
        if synced:
            return parse_lrc(synced)
    except Exception:
        pass

    search_params = urllib.parse.urlencode({
        "track_name": track["title"],
        "artist_name": track["artist"],
    })
    try:
        results = request_json("https://lrclib.net/api/search?" + search_params)
        if isinstance(results, list):
            # Prefer a synchronized result matching both artist and title.
            for item in results:
                if not item.get("syncedLyrics"):
                    continue
                if (item.get("trackName", "").casefold() == track["title"].casefold()
                        and item.get("artistName", "").casefold() == track["artist"].casefold()):
                    parsed = parse_lrc(item["syncedLyrics"])
                    if parsed:
                        return parsed
            # Otherwise use the first result that actually has timed lyrics.
            for item in results:
                if item.get("syncedLyrics"):
                    parsed = parse_lrc(item["syncedLyrics"])
                    if parsed:
                        return parsed
    except Exception:
        pass
    return []


def make_view(track, status, position, lyrics, message=""):
    width = max(40, min(console.size.width - 4, 92))
    title = Text("✦ N E O   L Y R I C S ✦", style="bold bright_magenta")
    subtitle = Text("ANIME EDITION  /  TYPEWRITER SYNC", style="bright_blue")

    heading = Text()
    heading.append(track["title"] if track else "Esperando a Spotify...", style="bold white")
    if track:
        heading.append("\n" + track["artist"], style="bright_magenta")

    body = []
    if not track:
        body.append(Align.center(Text("Abre Spotify y reproduce una canción.", style="bright_cyan")))
    elif message:
        body.append(Align.center(Text(message, style="yellow")))
    elif not lyrics:
        body.append(Align.center(Text("No se encontraron letras sincronizadas.", style="yellow")))
        body.append(Align.center(Text("Esta canción puede no tener letras con marcas de tiempo.", style="dim")))
    else:
        times = [item[0] for item in lyrics]
        index = bisect.bisect_right(times, position) - 1

        if index < 0:
            body.append(Align.center(Text("✧ La canción está por comenzar ✧", style="dim magenta")))
        else:
            line_start, line = lyrics[index]
            # Reveal the current lyric progressively until the next timestamp.
            if index + 1 < len(lyrics):
                line_end = lyrics[index + 1][0]
            else:
                line_end = line_start + max(2.0, min(6.0, len(line) * 0.12))

            interval = max(0.8, line_end - line_start)
            elapsed = max(0.0, position - line_start)
            # Keep a short visual lead-in, then reveal the complete line over its lyric interval.
            reveal_duration = max(1.0, min(interval * 0.88, max(1.5, len(line) * 0.105)))
            progress = min(1.0, elapsed / reveal_duration)
            visible_chars = min(len(line), int(progress * len(line)) + (1 if progress > 0 else 0))
            visible_line = line[:visible_chars]

            body.append(Text(""))
            body.append(Align.center(Text("✦", style="bold bright_magenta")))
            body.append(Align.center(Text(visible_line or " ", style="bold white")))
            body.append(Align.center(Text("◈  SHADOW SYNC  ◈", style="bold bright_blue")))
            body.append(Text(""))

    state = Text()
    state.append("● ", style="green" if status == "Playing" else "yellow")
    state.append(status or "Spotify no disponible", style="bold")
    if track and track["duration"]:
        state.append(f"     {int(position // 60):02}:{int(position % 60):02}", style="bright_magenta")
        state.append(f" / {int(track['duration'] // 60):02}:{int(track['duration'] % 60):02}", style="dim")

    footer = Text("ONE LINE  ·  LETTER-BY-LETTER  ·  CTRL+C TO EXIT", style="dim bright_blue")
    content = Group(
        Align.center(title),
        Align.center(subtitle),
        Text(""),
        Align.center(heading),
        Text(""),
        *body,
        Text(""),
        Align.center(state),
        Align.center(footer),
    )
    return Panel(
        content,
        width=width,
        border_style="bright_magenta",
        title="[bold bright_blue]✦ SYSTEM ONLINE ✦[/]",
        subtitle="[dim]SHADOW TERMINAL[/]",
        padding=(1, 2),
    )

def main():
    console.clear()
    current_key = None
    track = None
    lyrics = []
    last_fetch = 0
    status = ""
    position = 0.0
    try:
        with Live(make_view(None, "", 0, []), console=console,
                  refresh_per_second=12, screen=True) as live:
            while True:
                status = playerctl("status")
                new_track = get_track() if status else None
                if new_track:
                    key = (new_track["artist"], new_track["title"], new_track["album"])
                    if key != current_key:
                        current_key = key
                        track = new_track
                        lyrics = []
                        last_fetch = time.time()
                        live.update(make_view(track, status, 0, [], "Buscando letras sincronizadas..."))
                        lyrics = fetch_lyrics(track)
                else:
                    current_key = None
                    track = None
                    lyrics = []

                try:
                    position = float(playerctl("position") or 0)
                except ValueError:
                    position = 0.0

                live.update(make_view(track, status, position, lyrics))
                time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        console.print("\n[bold bright_magenta]✦ NEO-LYRICS desconectado. Hasta la próxima. ✦[/]")


if __name__ == "__main__":
    if not playerctl("--version"):
        console.print("[bold red]No se encontró playerctl. Instala el paquete playerctl.[/]")
        sys.exit(1)
    main()
