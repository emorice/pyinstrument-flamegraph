"""
Custom build hook to download and validate flamegraph.pl

Since the original is hosted on github we could also have simply used a
submodule, this is deliberately an exercise in packaging.
"""
import os
import hashlib
from typing import Any
from urllib.request import urlretrieve
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

COMMIT = "cd9ee4c4449775a2f867acf31c84b7fe4b132ad5"
URL = f"https://raw.githubusercontent.com/brendangregg/FlameGraph/{COMMIT}/flamegraph.pl"
TARGET = './pyinstrument_flamegraph/flamegraph.pl'
SHA256 = "c5d180a54401074ee844009ff5fca2c003af992bc9735fc27aaf4722e21f9455"

class DownloadFlamegraphBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]):
        del version
        del build_data
        urlretrieve(URL, TARGET)
        with open(TARGET, 'rb') as fd:
            obs_sha = hashlib.file_digest(fd, "sha256").hexdigest()
        if obs_sha != SHA256:
            raise RuntimeError('Bad checksum for flamegraph.pl')
        # https://stackoverflow.com/a/30463972
        mode = os.stat(TARGET).st_mode
        mode |= (mode & 0o444) >> 2    # copy R bits to X
        os.chmod(TARGET, mode)
