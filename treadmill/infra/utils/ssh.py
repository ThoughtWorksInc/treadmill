from urllib import request
from treadmill.infra import connection

my_ip = request.urlopen(
    'http://ip.42.pl/raw'
).read().decode('utf-8') + '/32'


def enable(group_id):
    conn = connection.Connection()
    conn.authorize_security_group_ingress(
        CidrIp=my_ip,
        FromPort=22,
        ToPort=22,
        GroupId=group_id,
        IpProtocol='tcp'
    )


def disable(group_id):
    conn = connection.Connection()
    conn.revoke_security_group_ingress(
        CidrIp=my_ip,
        FromPort=22,
        ToPort=22,
        GroupId=group_id,
        IpProtocol='tcp'
    )
