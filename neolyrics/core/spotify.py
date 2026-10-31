"""Cross-platform Spotify Desktop metadata and transport adapters.

Linux: MPRIS via playerctl. Windows: Windows Global System Media Transport
Controls (GSMTC) via the optional ``winsdk`` package.
"""
from __future__ import annotations
from dataclasses import dataclass
import asyncio
import platform
import shutil
import subprocess

@dataclass(frozen=True, slots=True)
class Track:
    artist: str
    title: str
    album: str = ""
    duration: float = 0.0
    art_url: str = ""
    track_id: str = ""

class SpotifyClient:
    def __init__(self, player: str = "spotify", timeout: float = 1.5):
        self.player, self.timeout = player, timeout
        self._win_session = None
        self._win_data = None

    @property
    def available(self) -> bool:
        if platform.system() == "Windows":
            try:
                import winsdk.windows.media.control  # noqa: F401
                return True
            except ImportError:
                return False
        return shutil.which("playerctl") is not None

    def _run(self, *args: str) -> str:
        if platform.system() == "Windows" or not shutil.which("playerctl"):
            return ""
        try:
            p = subprocess.run(["playerctl", "-p", self.player, *args], capture_output=True,
                text=True, timeout=self.timeout, check=True)
            return p.stdout.strip()
        except (subprocess.SubprocessError, OSError):
            return ""

    def _windows_refresh(self):
        """Read current Windows media session without blocking the UI for long."""
        async def read():
            from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as Manager
            manager = await Manager.request_async()
            sessions = list(manager.get_sessions())
            session = next((s for s in sessions if "spotify" in str(s.source_app_user_model_id).lower()), None)
            if session is None:
                self._win_session, self._win_data = None, None
                return
            props = await session.try_get_media_properties_async()
            playback = session.get_playback_info()
            timeline = session.get_timeline_properties()
            self._win_session = session
            self._win_data = (props, playback, timeline)
        try:
            asyncio.run(asyncio.wait_for(read(), timeout=max(2.5, self.timeout + 1)))
        except Exception:
            pass

    def _windows_status(self) -> str:
        self._windows_refresh()
        if not self._win_data: return ""
        status = str(self._win_data[1].playback_status)
        return "Playing" if "PLAYING" in status.upper() else ("Paused" if "PAUSED" in status.upper() else "Stopped")

    def status(self) -> str:
        return self._windows_status() if platform.system() == "Windows" else self._run("status")

    def track(self) -> Track | None:
        if platform.system() == "Windows":
            if not self._win_data: self._windows_refresh()
            if not self._win_data: return None
            props, _, timeline = self._win_data
            title = str(props.title or "").strip()
            if not title: return None
            artist = str(props.artist or "Artista desconocido")
            album = str(props.album_title or "")
            duration = max(0.0, (timeline.end_time - timeline.start_time).total_seconds())
            thumb = getattr(props, "thumbnail", None)
            art_url = ""
            if thumb and getattr(thumb, "uri", None): art_url = str(thumb.uri)
            return Track(artist, title, album, duration, art_url, f"{artist}|{title}|{album}")
        fmt = "{{artist}}|||{{title}}|||{{album}}|||{{mpris:length}}|||{{mpris:artUrl}}|||{{mpris:trackid}}"
        parts = self._run("metadata", "--format", fmt).split("|||")
        if len(parts) < 2 or not parts[1].strip(): return None
        try: duration = int(parts[3]) / 1_000_000 if len(parts) > 3 and parts[3] else 0.0
        except (ValueError, IndexError): duration = 0.0
        return Track(parts[0] or "Artista desconocido", parts[1], parts[2] if len(parts)>2 else "",
                     duration, parts[4] if len(parts)>4 else "", parts[5] if len(parts)>5 else "")

    def position(self) -> float:
        if platform.system() == "Windows":
            if not self._win_data: self._windows_refresh()
            if not self._win_data: return 0.0
            try: return max(0.0, (self._win_data[2].position - self._win_data[2].start_time).total_seconds())
            except Exception: return 0.0
        try: return max(0.0, float(self._run("position") or 0.0))
        except ValueError: return 0.0

    def _windows_command(self, command: str):
        async def run():
            if self._win_session is None: await self._windows_refresh_async()
            if self._win_session is None: return
            methods = {"play-pause": "try_toggle_play_pause_async", "next": "try_skip_next_async", "previous": "try_skip_previous_async"}
            await getattr(self._win_session, methods[command])()
        try: asyncio.run(run())
        except Exception: pass

    async def _windows_refresh_async(self):
        from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as Manager
        manager = await Manager.request_async()
        self._win_session = next((s for s in manager.get_sessions() if "spotify" in str(s.source_app_user_model_id).lower()), None)

    def _command(self, command: str):
        if platform.system() == "Windows": self._windows_command(command)
        else: self._run(command)
    def play_pause(self): self._command("play-pause")
    def next(self): self._command("next")
    def previous(self): self._command("previous")
