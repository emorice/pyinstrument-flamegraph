"""
Render with framegraph.pl
"""
import os
import math
import hashlib
import tempfile
import subprocess
import importlib.resources

from pyinstrument.renderers import FrameRenderer
from pyinstrument import processors

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

def print_log(frame, palette=None):
    """
    Helper to write the frames in flamegraph format
    """
    frames = [([], frame)]
    lines = []
    while frames:
        parent_stack, frame = frames.pop()
        item = f"{frame.function}\u2002\u2002{frame.file_path_short}:{frame.line_no}"
        if palette is not None and item not in palette:
            if frame.file_path_short is None:
                package = ''
            else:
                package = frame.file_path_short.partition('/')[0]
            palette[item] = color_from_string(package)
        stack = (*parent_stack, item)
        child_time = sum(f.time for f in frame.children)
        own_time = max(frame.time - child_time, 0.0)
        lines.append(
                f'{";".join(stack)} {own_time * 1000:f}'
            )
        frames.extend((stack, child) for child in frame.children)
    return lines

def print_palette(palette, file):
    """Write flamegraph palette file"""
    for frame, rgb in palette.items():
        print(f'{frame}->rgb({",".join(map(str, rgb))})', file=file)

class FlameGraphRenderer(FrameRenderer):
    """
    Render as flame graph
    """
    def render(self, session):
        """
        Write flamegraph inputs to a temporary directory, move there, run the
        packaged flamegraph and return the svg output
        """
        flamegraph_path = importlib.resources.files() / 'flamegraph.pl'
        frame = self.preprocess(session.root_frame())
        palette = {}
        lines = print_log(frame, palette=palette)
        # palette.map is hardcoded, so work in a tempdir
        with tempfile.TemporaryDirectory() as dirpath:
            with open(
                    os.path.join(dirpath, 'profile.log'),
                    'w', encoding='utf8') as fd:
                fd.write('\n'.join(lines) + '\n')
            with open(
                    os.path.join(dirpath, 'palette.map'),
                    'w', encoding='utf8') as fd:
                print_palette(palette, fd)
            with importlib.resources.as_file(flamegraph_path) as flamegraph_pl:
                svg = subprocess.check_output([
                    flamegraph_pl, '--cp', 'profile.log', '--countname', 'ms'
                    ], cwd=dirpath, encoding='utf8')
        return svg

    def default_processors(self):
        """
        List of processors.

        We mostly remove hiding small nodes
        """
        return [
                processors.remove_importlib,
                processors.remove_tracebackhide,
                processors.merge_consecutive_self_time,
                processors.aggregate_repeated_calls,
                processors.remove_unnecessary_self_time_nodes,
                # On a graph small nodes already take little space, so no need to
                # hide them
                # processors.remove_irrelevant_nodes,
                processors.remove_first_pyinstrument_frames_processor,
                processors.group_library_frames_processor,
                ]
