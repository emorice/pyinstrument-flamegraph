import os
from typing import Any
from urllib.request import urlretrieve
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

COMMIT = "cd9ee4c4449775a2f867acf31c84b7fe4b132ad5"
URL = f"https://raw.githubusercontent.com/brendangregg/FlameGraph/{COMMIT}/flamegraph.pl"
TARGET = './pyinstrument_flamegraph/flamegraph.pl'

class DownloadFlamegraphBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]):
        urlretrieve(URL, TARGET)
        # https://stackoverflow.com/a/30463972
        mode = os.stat(TARGET).st_mode
        mode |= (mode & 0o444) >> 2    # copy R bits to X
        os.chmod(TARGET, mode)
