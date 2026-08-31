"""
Directory entry point for Batocera and `python Pokemon-Game/`.

Batocera launches pygame ROMs as:
    pygame /userdata/roms/pygame/Pokemon-Game.pygame

`/usr/bin/pygame` is a Python interpreter. When the ROM is a folder, Python
looks for this file. Without it you get:
    can't find '__main__' module in '.../Pokemon-Game.pygame'
"""
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from main import start

if __name__ == "__main__":
    start()
