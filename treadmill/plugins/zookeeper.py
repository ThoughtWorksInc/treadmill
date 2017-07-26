"""
    Treadmill Zookeeper Plugin
"""
import kazoo.client
import kazoo.security

_ROLES = ['servers', 'admins', 'readers']


def connect(zkurl, connargs):
    """
    Connect to zookeeper
    """
    if not connargs.get('hosts'):
        connargs['hosts'] = zkurl[len('zookeeper://'):]

    if not connargs.get('sasl_data'):
        connargs['sasl_data'] = {
            'service': 'host',
            'mechanisms': ['GSSAPI']
        }

    return kazoo.client.KazooClient(**connargs)


def make_user_acl(user, perm):
    """
    Create user acl in zookeeper.
    """
    return kazoo.security.make_acl(
        scheme='sasl', credential=user, read='r' in perm,
        write='w' in perm, delete='d' in perm,
        create='c' in perm, admin='a' in perm
    )


def make_role_acl(role, perm):
    """
    Create role acl in zookeeper.
    """
    assert(role in _ROLES)

    return kazoo.security.make_acl(
        scheme='sasl', credential='role/{0}'.format(role),
        read='r' in perm, write='w' in perm,
        delete='d' in perm, create='c' in perm,
        admin='a' in perm
    )


def make_host_acl(host, perm):
    """
    Create host acl in zookeeper.
    """
    return kazoo.security.make_acl(
        scheme='sasl', credential='host/{0}'.format(host),
        read='r' in perm, write='w' in perm,
        delete='d' in perm, create='c' in perm,
        admin='a' in perm
    )
