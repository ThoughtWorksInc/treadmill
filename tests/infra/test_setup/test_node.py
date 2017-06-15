"""
Unit test for EC2 node setup.
"""

import unittest
import mock

from treadmill.infra.setup.node import Node


class NodeTest(unittest.TestCase):
    """Tests EC2 node setup."""

    @mock.patch('treadmill.infra.setup.node.Instance')
    def test_setup_node(self, InstanceMock):
        instance_mock = InstanceMock()
        instance_mock.instances = {
            'Instances': [{'InstanceId': 123}]
        }

        node = Node()
        node.setup()

        self.assertIsNotNone(node.instances)

    @mock.patch('treadmill.infra.setup.node.Instance')
    def test_setup_terminate(self, InstanceMock):
        node = Node()
        node.instances = InstanceMock()
        node.terminate()

        node.instances.terminate.assert_called_once()
