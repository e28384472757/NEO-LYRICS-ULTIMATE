import argparse
import sys

def build_parser():
    p=argparse.ArgumentParser(prog="neolyrics",description="NEO-LYRICS ULTIMATE — letras sincronizadas para Spotify")
    mode=p.add_mutually_exclusive_group(); mode.add_argument("--gui",action="store_true",help="Abrir interfaz gráfica HD (predeterminado)"); mode.add_argument("--terminal",action="store_true",help="Abrir modo terminal HD para Konsole (SIXEL/Chafa + Rich)")
    p.add_argument("--version",action="version",version="NEO-LYRICS ULTIMATE 1.2.0")
    return p

def main(argv=None):
    args=build_parser().parse_args(argv)
    if args.terminal:
        try:
            from neolyrics.terminal.main import main as run
            run(); return 0
        except ImportError as e: print(f"Falta una dependencia del modo terminal: {e}\nInstala rich.",file=sys.stderr); return 2
    try:
        from neolyrics.gui.main import main as run
        return run()
    except ImportError as e:
        print(f"No se pudo cargar la GUI: {e}\nInstala PySide6 o ejecuta neolyrics --terminal.",file=sys.stderr); return 2
