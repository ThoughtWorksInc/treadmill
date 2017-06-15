"""
Unit test for EC2 freeipa setup.
"""

import unittest
import mock

from treadmill.infra.setup.freeipa import FreeIPA


class FreeIPATest(unittest.TestCase):
    """Tests EC2 freeipa setup."""

    @mock.patch('treadmill.infra.setup.freeipa.Instance')
    def test_setup_freeipa(self, InstanceMock):
        instance_mock = InstanceMock()
        instance_mock.instances = {
            'Instances': [{'InstanceId': 123}]
        }

        freeipa = FreeIPA()
        freeipa.setup()

        self.assertIsNotNone(freeipa.instance)

    @mock.patch('treadmill.infra.setup.freeipa.Instance')
    def test_setup_terminate(self, InstanceMock):

        freeipa = FreeIPA()
        freeipa.instance = InstanceMock()
        freeipa.terminate()

        freeipa.instance.terminate.assert_called_once()
