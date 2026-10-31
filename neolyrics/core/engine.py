"""Shared polling engine for GUI and terminal frontends."""
from __future__ import annotations
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from .spotify import SpotifyClient, Track
from .lyrics import LRCLibClient, LyricLine
from .synchronizer import Synchronizer, SyncFrame

@dataclass
class EngineState:
    connected: bool = False
    status: str = "Stopped"
    track: Track | None = None
    position: float = 0.0
    lyrics: list[LyricLine] = field(default_factory=list)
    lyrics_loading: bool = False
    message: str = "Abre Spotify y reproduce una canción."
    frame: SyncFrame | None = None

class LyricsEngine:
    def __init__(self, spotify=None, lyrics_client=None, synchronizer=None):
        self.spotify = spotify or SpotifyClient()
        self.lyrics_client = lyrics_client or LRCLibClient()
        self.synchronizer = synchronizer or Synchronizer()
        self.state = EngineState()
        self._key = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="neo-lyrics")
        self._future = None
        self._lock = RLock()

    def _load_done(self, future, key):
        try: lines = future.result()
        except Exception: lines = []
        with self._lock:
            if key != self._key: return
            self.state.lyrics = lines
            self.state.lyrics_loading = False
            self.state.message = "" if lines else "No hay letras sincronizadas disponibles para esta canción."

    def tick(self) -> EngineState:
        status = self.spotify.status()
        track = self.spotify.track() if status else None
        position = self.spotify.position() if status else 0.0
        with self._lock:
            self.state.connected = bool(status or track)
            self.state.status = status or "Stopped"
            if track:
                key = (track.track_id, track.artist.casefold(), track.title.casefold(), track.album.casefold())
                if key != self._key:
                    self._key = key
                    self.state.track = track
                    self.state.position = position
                    self.state.lyrics = []
                    self.state.lyrics_loading = True
                    self.state.message = "Buscando letras sincronizadas…"
                    self._future = self._executor.submit(self.lyrics_client.fetch, track)
                    self._future.add_done_callback(lambda f, k=key: self._load_done(f, k))
            else:
                self._key = None
                self.state.track = None
                self.state.lyrics = []
                self.state.lyrics_loading = False
                self.state.message = "Spotify no está reproduciendo."
            self.state.position = position
            self.state.frame = self.synchronizer.frame(self.state.lyrics, position)
            return self.snapshot()

    def snapshot(self) -> EngineState:
        with self._lock:
            s = self.state
            return EngineState(s.connected, s.status, s.track, s.position, list(s.lyrics),
                               s.lyrics_loading, s.message, s.frame)

    def close(self): self._executor.shutdown(wait=False, cancel_futures=True)
