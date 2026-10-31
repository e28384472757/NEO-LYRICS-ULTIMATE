# NEO-LYRICS ULTIMATE — Design Direction

## Overview

Product surface: a dual-mode synchronized Spotify lyrics player for Arch Linux. The terminal mode is designed for Konsole first. Its signature is a real bitmap illustration rendered through terminal graphics protocols, with synchronized text kept crisp and readable below it. Pixel graphics are preferred over converting the full illustration into character blocks.

## Colors

- Void: `#07050D` — terminal and application base.
- Obsidian: `#100A1B` — structural surfaces.
- Royal violet: `#A855F7` — brand and active lyric emphasis.
- Electric blue: `#60A5FA` — secondary status and technical metadata.
- Moonlight: `#F3EAFF` — primary lyric and track text.
- Muted lilac: `#A99ABF` — supporting metadata.

## Typography

- Display: `DejaVu Serif`, with available gothic serif fonts as a local enhancement only.
- Body: `DejaVu Sans` for the GUI and terminal emulator font for terminal output.
- Utility: `monospace` for timestamps, progress, and technical status.
- Terminal lyrics use bold high-contrast text; terminal font size is controlled by Konsole, not by the application.

## Layout

The terminal reserves a static upper region for the bundled 1672 × 941 artwork, rendered with Chafa's detected pixel protocol (SIXEL in Konsole when available). A live Rich panel below it contains track metadata, one primary lyric line, playback position, progress, and a violet spectrum motif. On terminals without bitmap graphics, Chafa falls back to 24-bit sextant symbols.

## Elevation & Depth

The GUI uses a dark image-backed surface with subtle violet overlays. Terminal surfaces rely on contrast and thin violet framing rather than simulated shadows.

## Shapes

Gothic ornamental lines and restrained panel framing. Avoid excessive nested boxes that reduce terminal lyric area.

## Components

- Live lyric: one line only, revealed using the shared synchronizer's typewriter frame.
- Playback status: explicit connected/disconnected state plus Playing/Paused status.
- Progress: true track-relative progress from MPRIS position and duration.
- Terminal artwork: protocol-aware pixel image; truecolor symbol fallback.

## Do's and Don'ts

- Do use SIXEL/Kitty/iTerm2 bitmap protocols when supported; retain a legible fallback elsewhere.
- Do keep all music timing and lyric state in the shared `LyricsEngine`.
- Do not describe a text mosaic as HD or promise pixel quality on terminals without bitmap support.
- Do not paint terminal backgrounds with opaque blocks over the pixel artwork.
- Do not sacrifice lyric contrast for decorative effects.
