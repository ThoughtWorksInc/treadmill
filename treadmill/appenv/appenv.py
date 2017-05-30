"""Application environment."""

import abc
import logging
import os
import socket

import six

from treadmill import fs
from treadmill import watchdog


_LOGGER = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class AppEnvironment(object):
    """Treadmill application environment.

    :param root:
        Path to the root directory of the Treadmill environment
    :type root:
        `str`
    :param host_ip:
        Optional ip address of the host
    :type host_ip:
        `str`
    """

    __slots__ = (
        'app_types',
        'apps_dir',
        'archives_dir',
        'cache_dir',
        'cleanup_dir',
        'init_dir',
        'host_ip',
        'metrics_dir',
        'pending_cleanup_dir',
        'root',
        'running_dir',
        'app_events_dir',
        'watchdogs',
        'watchdog_dir',
    )

    APPS_DIR = 'apps'
    ARCHIVES_DIR = 'archives'
    CACHE_DIR = 'cache'
    CLEANUP_DIR = 'cleanup'
    INIT_DIR = 'init'
    PENDING_CLEANUP_DIR = 'pending_cleanup'
    RUNNING_DIR = 'running'
    METRICS_DIR = 'metrics'
    WATCHDOG_DIR = 'watchdogs'
    APP_EVENTS_DIR = 'appevents'

    def __init__(self, root, host_ip=None):
        self.root = root

        self.apps_dir = os.path.join(self.root, self.APPS_DIR)
        self.watchdog_dir = os.path.join(self.root, self.WATCHDOG_DIR)
        self.running_dir = os.path.join(self.root, self.RUNNING_DIR)
        self.cache_dir = os.path.join(self.root, self.CACHE_DIR)
        self.cleanup_dir = os.path.join(self.root, self.CLEANUP_DIR)
        self.app_events_dir = os.path.join(self.root, self.APP_EVENTS_DIR)
        self.metrics_dir = os.path.join(self.root, self.METRICS_DIR)
        self.archives_dir = os.path.join(self.root, self.ARCHIVES_DIR)
        self.init_dir = os.path.join(self.root, self.INIT_DIR)
        self.pending_cleanup_dir = os.path.join(self.root,
                                                self.PENDING_CLEANUP_DIR)

        if host_ip is not None:
            self.host_ip = host_ip
        elif os.environ.get('TREADMILL_NODE_IP', None):
            self.host_ip = os.environ.get('TREADMILL_NODE_IP')
        else:
            hostname = socket.gethostname()
            self.host_ip = socket.gethostbyname(hostname)

        self.watchdogs = watchdog.Watchdog(self.watchdog_dir)

        fs.mkdir_safe(self.apps_dir)
        fs.mkdir_safe(self.watchdog_dir)
        fs.mkdir_safe(self.running_dir)
        fs.mkdir_safe(self.cache_dir)
        fs.mkdir_safe(self.cleanup_dir)
        fs.mkdir_safe(self.app_events_dir)
        fs.mkdir_safe(self.metrics_dir)
        fs.mkdir_safe(self.archives_dir)

    @abc.abstractmethod
    def initialize(self):
        """One time initialization of the Treadmill environment."""
        pass
