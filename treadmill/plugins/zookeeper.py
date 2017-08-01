"""
    Treadmill Zookeeper Plugin
"""
import kazoo.client


def connect(zkurl, **connargs):
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
