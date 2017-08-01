"""
Unit test for zookeeper plugin
"""

import unittest
import mock
from treadmill.plugins.zookeeper import connect


class ZookeeperTest(unittest.TestCase):
    @mock.patch('kazoo.client.KazooClient')
    def test_connect_without_connargs(self, kazooClientMock):
        zkurl = 'zookeeper://foo@123:21'

        connect(zkurl, {})

        kazooClientMock.assert_called_once_with(
            hosts='foo@123:21',
            sasl_data={
                'service': 'host',
                'mechanisms': ['GSSAPI']
            })

    @mock.patch('kazoo.client.KazooClient')
    def test_connect_with_connargs(self, kazooClientMock):
        zkurl = 'zookeeper://foobar:123'
        connargs = {
            'hosts': 'foobar:123',
            'sasl_data': {
                'service': 'foo',
                'mechanisms': 'bar'
            }
        }

        connect(zkurl, connargs)

        kazooClientMock.assert_called_once_with(
            hosts='foobar:123',
            sasl_data={
                'service': 'foo',
                'mechanisms': 'bar'
            })
