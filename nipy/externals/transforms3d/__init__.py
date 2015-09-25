""" Placeholder for removed transforms3d code
"""

import warnings

warnings.warn(DeprecationWarning(
    "This module (nipy.externals.tranforms3d) is deprecated."
    "It just imports from the `transforms3d` package.  Please update your "
    "code to import directly from transforms3d"),
    stacklevel=2)

from . import quaternions
