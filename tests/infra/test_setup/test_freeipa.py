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
        InstancesMock.create = mock.Mock(return_value=['foo'])

        freeipa = FreeIPA()
        freeipa.setup(
            name='freeipa',
            image_id='foo-123',
            count=1,
            subnet_id=123
        )

        self.assertEqual(freeipa.instances, ['foo'])
        InstancesMock.create.assert_called_once_with(
            image_id='foo-123',
            name='freeipa',
            count=1,
            subnet_id=123
        )

    @mock.patch('treadmill.infra.setup.freeipa.instances.Instances')
    def test_freeipa_terminate(self, InstancesMock):
        freeipa = FreeIPA()
        freeipa.instances = InstancesMock()
        freeipa.terminate()

        freeipa.instances.terminate.assert_called_once()
