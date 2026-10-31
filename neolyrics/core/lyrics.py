"""LRCLIB client and tolerant LRC parser."""
from __future__ import annotations
from dataclasses import dataclass
import re
import urllib.parse
import urllib.request
import json
from typing import Iterable

_TIME = re.compile(r"\[(\d{1,3}):(\d{2})(?:[.:](\d{1,3}))?\]")

@dataclass(frozen=True, slots=True)
class LyricLine:
    timestamp: float
    text: str


def parse_lrc(source: str) -> list[LyricLine]:
    """Parse LRC timestamps, including multiple timestamps per line."""
    result: list[LyricLine] = []
    for raw in source.splitlines():
        stamps = list(_TIME.finditer(raw))
        if not stamps:
            continue
        lyric = _TIME.sub("", raw).strip()
        if not lyric or lyric.startswith(("[ar:", "[ti:", "[al:", "[by:", "[re:", "[ve:")):
            continue
        for match in stamps:
            minute, second, fraction = match.groups()
            frac = float("0." + fraction) if fraction else 0.0
            result.append(LyricLine(int(minute) * 60 + int(second) + frac, lyric))
    result.sort(key=lambda line: line.timestamp)
    return result

class LRCLibClient:
    BASE = "https://lrclib.net/api"
    def __init__(self, timeout: float = 7.0, user_agent: str = "NEO-LYRICS-ULTIMATE/1.0 (Linux lyrics client)"):
        self.timeout, self.user_agent = timeout, user_agent

    def _get_json(self, endpoint: str, params: dict) -> object:
        url = f"{self.BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def fetch(self, track) -> list[LyricLine]:
        params = {"artist_name": track.artist, "track_name": track.title}
        if track.album: params["album_name"] = track.album
        if track.duration and track.duration > 0: params["duration"] = str(round(track.duration))
        try:
            data = self._get_json("get", params)
            synced = data.get("syncedLyrics") if isinstance(data, dict) else None
            parsed = parse_lrc(synced or "")
            if parsed: return parsed
        except Exception:
            pass
        try:
            results = self._get_json("search", {"track_name": track.title, "artist_name": track.artist})
            if isinstance(results, list):
                ranked = sorted(results, key=lambda x: (
                    x.get("trackName", "").casefold() == track.title.casefold(),
                    x.get("artistName", "").casefold() == track.artist.casefold(),
                    bool(x.get("syncedLyrics"))), reverse=True)
                for item in ranked:
                    parsed = parse_lrc(item.get("syncedLyrics") or "")
                    if parsed: return parsed
        except Exception:
            pass
        return []
