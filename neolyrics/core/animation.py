"""Small presentation helpers shared by frontends."""
def format_time(seconds: float) -> str:
    seconds = max(0, int(seconds or 0))
    return f"{seconds//60:02d}:{seconds%60:02d}"

def progress_fraction(position: float, duration: float) -> float:
    return min(1.0, max(0.0, position / duration)) if duration > 0 else 0.0
