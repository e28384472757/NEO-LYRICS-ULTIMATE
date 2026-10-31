import unittest
from types import SimpleNamespace

from neolyrics.terminal.main import _graphics_protocol, render


class TestTerminalHD(unittest.TestCase):
    def test_protocol_detection(self):
        self.assertEqual(_graphics_protocol(b"\x1bPq..."), "SIXEL / PIXEL GRAPHICS")
        self.assertEqual(_graphics_protocol(b"\x1b_Ga=T;"), "KITTY PIXEL GRAPHICS")
        self.assertEqual(_graphics_protocol(b"\x1b]1337;File=inline=1"), "ITERM2 PIXEL GRAPHICS")
        self.assertEqual(_graphics_protocol(b"\x1b[38;2;170;90;255m"), "TRUECOLOR / SEXTANT FALLBACK")

    def test_render_without_track_has_waiting_state(self):
        state = SimpleNamespace(
            track=None, connected=False, status="Stopped", position=0.0,
            lyrics=[], lyrics_loading=False, message="Esperando", frame=None,
        )
        panel = render(state, 4)
        self.assertIsNotNone(panel)

    def test_render_with_track_and_synced_line(self):
        track = SimpleNamespace(title="Test Song", artist="Test Artist", album="Test Album", duration=180.0)
        frame = SimpleNamespace(index=0, visible="Hello", line="Hello")
        state = SimpleNamespace(
            track=track, connected=True, status="Playing", position=5.0,
            lyrics=[object()], lyrics_loading=False, message="", frame=frame,
        )
        panel = render(state, 7)
        self.assertIsNotNone(panel)


if __name__ == "__main__":
    unittest.main()
