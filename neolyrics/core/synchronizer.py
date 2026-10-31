"""Time-to-line mapping and deterministic typewriter reveal."""
from bisect import bisect_right
from dataclasses import dataclass
from .lyrics import LyricLine

@dataclass(frozen=True, slots=True)
class SyncFrame:
    index: int
    line: str
    visible: str
    progress: float
    start: float
    end: float

class Synchronizer:
    def __init__(self, chars_per_second: float = 18.0, max_reveal_fraction: float = .88):
        self.chars_per_second = max(1.0, chars_per_second)
        self.max_reveal_fraction = min(.98, max(.2, max_reveal_fraction))

    def frame(self, lyrics: list[LyricLine], position: float) -> SyncFrame | None:
        if not lyrics: return None
        times = [x.timestamp for x in lyrics]
        index = bisect_right(times, max(0.0, position)) - 1
        if index < 0: return SyncFrame(-1, "", "", 0.0, 0.0, lyrics[0].timestamp)
        line = lyrics[index]
        end = lyrics[index + 1].timestamp if index + 1 < len(lyrics) else line.timestamp + max(3.0, len(line.text)/self.chars_per_second)
        interval = max(.15, end - line.timestamp)
        reveal_duration = min(interval * self.max_reveal_fraction, max(.45, len(line.text)/self.chars_per_second))
        progress = min(1.0, max(0.0, (position-line.timestamp)/max(.15, reveal_duration)))
        count = min(len(line.text), int(len(line.text)*progress + (1 if progress > 0 else 0)))
        return SyncFrame(index, line.text, line.text[:count], progress, line.timestamp, end)
