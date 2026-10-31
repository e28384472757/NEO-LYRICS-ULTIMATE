# Changelog

## 1.1.0 — Terminal HD

- Replaced the terminal's character-mosaic backdrop with Chafa's automatic bitmap-protocol output (SIXEL/Kitty/iTerm2 when the terminal supports it).
- Added a truecolor sextant fallback for terminals without bitmap graphics.
- Kept the artwork in a static region and updated only the playback/lyrics panel below it, avoiding repeated image conversion during playback.
- Retained the shared LyricsEngine, LRCLIB lookup, MPRIS tracking, and typewriter synchronization.
- Fixed the Arch installer so it removes a stale symlink that points to the `neolyrics/` package directory before installing the executable launcher.
- Added terminal presentation tests and `DESIGN.md`.
- Replaced the original 786 × 461 wallpaper with a 1672 × 941 gothic anime artwork; preserved the previous asset under `legacy/assets/`.
