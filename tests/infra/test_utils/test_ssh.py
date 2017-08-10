import unittest
import mock
from treadmill.infra.utils import ssh

class SSHTest(unittest.TestCase):
    @mock.patch('treadmill.infra.connection.Connection')
    def test_enable(self, connectionMock):
        ssh.conn = connectionMock()
        ssh.my_ip = '127.0.0.1'

        ssh.enable(group_id='sg-123')

        ssh.conn.authorize_security_group_ingress.assert_called_once_with(
            CidrIp='127.0.0.1',
            FromPort=22,
            ToPort=22,
            GroupId='sg-123',
            IpProtocol='tcp'
        )

    @mock.patch('treadmill.infra.connection.Connection')
    def test_disable(self, connectionMock):
        ssh.conn = connectionMock()
        ssh.my_ip = '127.0.0.1'

        ssh.disable(group_id='sg-123')

        ssh.conn.revoke_security_group_ingress.assert_called_once_with(
            CidrIp='127.0.0.1',
            FromPort=22,
            ToPort=22,
            GroupId='sg-123',
            IpProtocol='tcp'
        )
