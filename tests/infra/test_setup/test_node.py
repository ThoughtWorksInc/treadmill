"""
Unit test for EC2 node.
"""

import unittest
import mock

from treadmill.infra.setup.node import Node


class NodeTest(unittest.TestCase):
    """Tests EC2 Node"""

    @mock.patch('treadmill.infra.instances.Instances')
    @mock.patch('treadmill.infra.connection.Connection')
    def test_hostnames_for_multiple(self, ConnectionMock, InstancesMock):
        InstancesMock.get_hostnames_by_roles = mock.Mock(return_value={
            'IPA': 'ipa-hostname',
            'LDAP': 'ldap-hostname',
        })

        node = Node(
            vpc_id='vpc-id',
            name='node'
        )
        _ldap_hostname, _ipa_hostname = node.hostnames_for(
            roles=['LDAP', 'IPA']
        )

        self.assertEqual(_ldap_hostname, 'ldap-hostname')
        self.assertEqual(_ipa_hostname, 'ipa-hostname')

    @mock.patch('treadmill.infra.instances.Instances')
    @mock.patch('treadmill.infra.connection.Connection')
    def test_hostnames_for_single(self, ConnectionMock, InstancesMock):
        InstancesMock.get_hostnames_by_roles = mock.Mock(return_value={
            'IPA': 'ipa-hostname',
        })

        node = Node(
            vpc_id='vpc-id',
            name='node'
        )
        _ipa_hostname, = node.hostnames_for(
            roles=['IPA']
        )

        self.assertEqual(_ipa_hostname, 'ipa-hostname')

    @mock.patch('treadmill.infra.instances.Instances')
    @mock.patch('treadmill.infra.connection.Connection')
    def test_hostnames_for_none(self, ConnectionMock, InstancesMock):
        InstancesMock.get_hostnames_by_roles = mock.Mock(return_value={})

        node = Node(
            vpc_id='vpc-id',
            name='node'
        )

        self.assertIsNone(node.hostnames_for(roles=['IPA']))
        self.assertIsNone(node.hostnames_for(roles=[]))

    @mock.patch('treadmill.infra.instances.Instances')
    @mock.patch('treadmill.infra.connection.Connection')
    @mock.patch('treadmill.infra.vpc.VPC')
    def test_node_destroy_by_instance_id(self, VPCMock,
                                         ConnectionMock, InstancesMock):
        _instances_obj_mock = mock.Mock()
        InstancesMock.get = mock.Mock(return_value=_instances_obj_mock)

        node = Node(
            vpc_id='vpc-id',
            name='node'
        )
        node.destroy(
            instance_id='instance-id'
        )

        InstancesMock.get.assert_called_once_with(ids=['instance-id'])
        _instances_obj_mock.terminate.assert_called_once_with()

    @mock.patch('treadmill.infra.instances.Instances')
    @mock.patch('treadmill.infra.connection.Connection')
    @mock.patch('treadmill.infra.vpc.VPC')
    def test_node_destroy_by_instance_name(self, VPCMock,
                                           ConnectionMock, InstancesMock):
        _instances_obj_mock = mock.Mock()
        InstancesMock.get = mock.Mock(return_value=_instances_obj_mock)

        node = Node(
            vpc_id='vpc-id',
            name='node-instance-name'
        )
        node.destroy()

        InstancesMock.get.assert_called_once_with(
            filters=[
                {
                    'Name': 'tag-key',
                    'Values': ['Name']
                },
                {
                    'Name': 'tag-value',
                    'Values': ['node-instance-name']
                },
            ]
        )
        _instances_obj_mock.terminate.assert_called_once_with()

    @mock.patch('treadmill.infra.instances.Instances')
    @mock.patch('treadmill.infra.connection.Connection')
    @mock.patch('treadmill.infra.vpc.VPC')
    def test_node_destroy_without_identifier_should_do_nothing(
            self,
            VPCMock,
            ConnectionMock,
            InstancesMock
    ):
        InstancesMock.get = mock.Mock()
        node = Node(
            vpc_id='vpc-id',
            name=None
        )
        node.destroy()

        InstancesMock.get.assert_not_called()
