# FlameGraph renderer for Pyinstrument

FrameRenderer plugin for [Pyinstrument](https://github.com/joerick/pyinstrument), which generates interactive SVG flamegraphs with the original `flamegraph.pl` generator of [FlameGraph](https://github.com/brendangregg/FlameGraph/). Installing this package will download `flamegraph.pl` as an automated installation step, by installing or using pyinstrument-flamegraph you also agree to the original license of FlameGraph.

Installation:
--
```
pip install git+https://github.com/emorice/pyinstrument-flamegraph
```

Usage:
--
This package provides a `pyinstrument.FlameGraphRenderer` class that can be used with Pyinstrument's `-r` renderer selector option, for instance:
```
pyinstrument -o profile.svg -r pyinstrument_flamegraph.FlameGraphRenderer script.py
```
You can then open `profile.svg` in your browser and explore. Frames are deterministically colored by module name.
