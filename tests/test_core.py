import unittest
from types import SimpleNamespace
from neolyrics.core.lyrics import parse_lrc
from neolyrics.core.synchronizer import Synchronizer
from neolyrics.core.animation import format_time, progress_fraction

class TestLRC(unittest.TestCase):
    def test_parse_centiseconds_and_multiple_stamps(self):
        got=parse_lrc('[00:01.50][00:03.25]Hello\n[ar:Artist]\n[00:05]World')
        self.assertEqual([(round(x.timestamp,2),x.text) for x in got],[(1.5,'Hello'),(3.25,'Hello'),(5.0,'World')])
    def test_empty_and_invalid(self): self.assertEqual(parse_lrc('metadata only\n[00:01]'),[])
    def test_sorted(self):
        got=parse_lrc('[00:03]B\n[00:01]A'); self.assertEqual([x.text for x in got],['A','B'])

class TestSync(unittest.TestCase):
    def setUp(self): self.lines=parse_lrc('[00:01.00]abcdefghij\n[00:03.00]next')
    def test_before_first_line(self): self.assertEqual(Synchronizer().frame(self.lines,0).index,-1)
    def test_line_selection(self): self.assertEqual(Synchronizer().frame(self.lines,3.1).line,'next')
    def test_typewriter_progresses(self):
        sync=Synchronizer(chars_per_second=5)
        early=sync.frame(self.lines,1.2); later=sync.frame(self.lines,2.0)
        self.assertLess(len(early.visible),len(later.visible))
    def test_format(self): self.assertEqual(format_time(125),'02:05'); self.assertEqual(progress_fraction(5,10),.5)


class TestSpotifyParsing(unittest.TestCase):
    def test_metadata_fields_preserve_empty_album(self):
        from neolyrics.core.spotify import SpotifyClient
        client=SpotifyClient()
        client._run=lambda *args: "Artist|||Song||||||180000000|||file:///tmp/cover.png|||trackid"
        track=client.track()
        self.assertEqual(track.artist,'Artist')
        self.assertEqual(track.title,'Song')
        self.assertEqual(track.album,'')
        self.assertEqual(track.duration,180.0)
        self.assertEqual(track.art_url,'file:///tmp/cover.png')

class FakeSpotify:
    def __init__(self):
        self.current=SimpleNamespace(artist='Artist',title='Song',album='Album',duration=180.0,art_url='',track_id='id')
        self.playback='Playing'; self.pos=2.0
    def status(self): return self.playback
    def track(self): return self.current
    def position(self): return self.pos

class FakeLyrics:
    def fetch(self, track): return parse_lrc('[00:01]first line\n[00:03]second line')

class TestEngine(unittest.TestCase):
    def test_shared_engine_updates_track_and_lyrics(self):
        import time
        from neolyrics.core.engine import LyricsEngine
        spotify=FakeSpotify(); engine=LyricsEngine(spotify=spotify,lyrics_client=FakeLyrics())
        try:
            state=engine.tick(); self.assertEqual(state.track.title,'Song'); self.assertTrue(state.lyrics_loading or state.lyrics)
            for _ in range(20):
                time.sleep(.01); state=engine.tick()
                if state.lyrics: break
            self.assertEqual(state.lyrics[0].text,'first line')
            spotify.pos=4.0; state=engine.tick(); self.assertEqual(state.frame.line,'second line')
            spotify.playback='Paused'; state=engine.tick(); self.assertEqual(state.status,'Paused')
            spotify.current=SimpleNamespace(artist='Other',title='New song',album='',duration=100.0,art_url='',track_id='new')
            state=engine.tick(); self.assertEqual(state.track.title,'New song')
        finally: engine.close()

if __name__=='__main__': unittest.main()
