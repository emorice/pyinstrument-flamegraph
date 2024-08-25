"""
Test superficial function
"""
import time
import pyinstrument
import pyinstrument_flamegraph

def test_produces_svg():
    """
    Core functionality
    """
    profiler = pyinstrument.Profiler()
    profiler.start()
    try:
        time.sleep(0.1)
    finally:
        profiler.stop()
    text = profiler.output(pyinstrument_flamegraph.FlameGraphRenderer(show_all=True))

    assert 'svg' in text.lower()

def test_contextmanager_produces_svg(tmp_path):
    """
    Context manager helper
    """
    path = tmp_path / "test.svg"
    with pyinstrument_flamegraph.flamegraph(path):
        time.sleep(0.1)

    with open(path, 'r', encoding='utf8') as stm:
        text = stm.read()
    assert 'svg' in text.lower()
