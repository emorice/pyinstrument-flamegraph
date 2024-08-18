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

def color(h, s):
    """Rotating color"""
    # Uniform s means a lot of neutral colors, bias towards saturated
    s = .5 + .5 * s
    v = .75
    # Rotate through r/g/b according to h, shrink towards grey according
    # to s, and keep v constant
    theta = 2 * math.pi * h
    red   = int(256 * v * (1 - .5 * s * (1 - math.cos(theta              ))))
    green = int(256 * v * (1 - .5 * s * (1 - math.cos(theta - 2*math.pi/3))))
    blue  = int(256 * v * (1 - .5 * s * (1 - math.cos(theta + 2*math.pi/3))))
    return red, green, blue

def color_from_string(string):
    """Random h and s"""
    md5 = hashlib.md5(string.encode('utf8')).digest()
    h_value = int.from_bytes(md5[:2]) / 2**16
    s_value = int.from_bytes(md5[2:4]) / 2**16
    return color(h_value, s_value)

def print_log(frame, stack=None, palette=None):
    """
    Recursive helper to write the frames
    """
    if stack is None:
        stack = []
    item = f"{frame.function}:{frame.file_path_short}:{frame.line_no}"
    if palette is not None and item not in palette:
        package = frame.file_path_short.partition('/')[0]
        palette[item] = color_from_string(package)
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
                    flamegraph_pl, '--cp', 'profile.log', '--countname', 'ms'
                    ], encoding='utf8')
            finally:
                os.chdir(pwd)
        return svg
