"""
Test superficial function
"""
import time
import pyinstrument
import pyinstrument_flamegraph

def test_produces_svg():
    profiler = pyinstrument.Profiler()
    profiler.start()
    try:
        time.sleep(0.1)
    finally:
        profiler.stop()
    text = profiler.output(pyinstrument_flamegraph.FlameGraphRenderer(show_all=True))

    assert 'svg' in text.lower()
