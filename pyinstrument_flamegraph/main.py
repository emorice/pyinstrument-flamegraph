"""
Render with framegraph.pl
"""
import os
import math
import hashlib
import tempfile
import subprocess
import importlib.resources

from pyinstrument.renderers import JSONRenderer

def color(x):
    """Rotating color"""
    theta = 2 * math.pi * x
    red = int(128 * (1 + .999 * math.cos(theta)))
    green = int(128 * (1 + .999 * math.cos(theta - 2*math.pi/3)))
    blue = int(128 * (1 + .999 * math.cos(theta + 2*math.pi/3)))
    return red, green, blue

def print_log(frame, stack=None, palette=None):
    """
    Recursive helper to write the frames
    """
    if stack is None:
        stack = []
    item = f"{frame.function}:{frame.file_path_short}:{frame.line_no}"
    if palette is not None and item not in palette:
        x_color = int.from_bytes(
                hashlib.md5(
                    frame.file_path_short.encode('utf8')
                ).digest()[-2:]
                ) / 2**16
        palette[item] = color(x_color)
    stack.append(item)
    total_time = frame.time
    child_time = sum(f.time for f in frame.children)
    own_time = max(total_time - child_time, 0.0)
    lines = [
            f'{";".join(stack)} {own_time * 1000:f}'
        ]
    for child in frame.children:
        lines.extend(print_log(child, stack, palette))
    stack.pop()
    return lines

def print_palette(palette, file):
    """Write flamegraph palette file"""
    for frame, rgb in palette.items():
        print(f'{frame}->rgb({",".join(map(str, rgb))})', file=file)

class FlameGraphRenderer(JSONRenderer):
    """
    Initialize base json renderer but set show_all to True by default
    """
    def __init__(self, *args, show_all=True, **kwargs):
        super().__init__(*args, show_all=show_all, **kwargs)

    def render(self, session):
        """
        Write flamegraph inputs to a temporary directory, move there, run the
        packaged flamegraph and return the svg output
        """
        flamegraph_pl = importlib.resources.files() / 'flamegraph.pl'
        frame = self.preprocess(session.root_frame())
        palette = {}
        lines = print_log(frame, palette=palette)
        pwd = os.getcwd()
        with tempfile.TemporaryDirectory() as dirpath:
            os.chdir(dirpath)
            try:
                with open('profile.log', 'w', encoding='utf8') as fd:
                    fd.write('\n'.join(lines) + '\n')
                # Palette.map is hardcoded, hence the temp dir chdir
                with open('palette.map', 'w', encoding='utf8') as fd:
                    print_palette(palette, fd)
                svg = subprocess.check_output([
                    flamegraph_pl, '--cp', 'profile.log'
                    ], encoding='utf8')
            finally:
                os.chdir(pwd)
        return svg
