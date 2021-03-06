"""Windows application environment."""

import logging

from . import appenv


_LOGGER = logging.getLogger(__name__)


class WindowsAppEnvironment(appenv.AppEnvironment):
    """Windows Treadmill application environment.

    :param root:
        Path to the root directory of the Treadmill environment
    :type root:
        `str`
    """

    def __init__(self, root):
        super(WindowsAppEnvironment, self).__init__(root)

    def initialize(self, _params):
        """One time initialization of the Treadmill environment."""
        _LOGGER.info('Initializing once.')
