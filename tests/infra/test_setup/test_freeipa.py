"""
Unit test for EC2 freeipa setup.
"""

import unittest
import mock

from treadmill.infra.setup.freeipa import FreeIPA


class FreeIPATest(unittest.TestCase):
    """Tests EC2 freeipa setup."""

    @mock.patch('treadmill.infra.setup.freeipa.instances.Instances')
    def test_setup_freeipa(self, InstancesMock):
        instances_mock = InstancesMock()
        instances_mock.instances = ['foo']

        freeipa = FreeIPA()
        freeipa.setup(
            name='freeipa',
            image_id='foo-123',
            count=1,
            subnet_id=123
        )

        self.assertIsNotNone(freeipa.instances)

    @mock.patch('treadmill.infra.setup.freeipa.instances.Instances')
    def test_setup_terminate(self, InstancesMock):

        freeipa = FreeIPA()
        freeipa.instances = InstancesMock()
        freeipa.terminate()

        freeipa.instances.terminate.assert_called_once()
