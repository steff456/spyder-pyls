# Copyright 2017 Palantir Technologies, Inc.
import os
from future.standard_library import install_aliases
import pluggy
from ._version import __version__

__version__ = __version__
install_aliases()
PYLS = 'pyls'
SPYDER_PYLS = True

hookspec = pluggy.HookspecMarker(PYLS)
hookimpl = pluggy.HookimplMarker(PYLS)

IS_WIN = os.name == 'nt'
