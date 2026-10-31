# Contributing

1. Create a feature branch.
2. Keep platform-specific integrations behind adapters in `neolyrics/core/spotify.py`.
3. Add tests for parsing, synchronization, and platform-independent behavior.
4. Run `python -m compileall -q neolyrics` and `python -m pytest -q`.
5. Describe tested operating systems and versions in the pull request.

Do not include Spotify credentials, personal logs, copyrighted lyric dumps, or private account data in issues or pull requests.
