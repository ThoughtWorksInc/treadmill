#!/bin/bash -e

DOMAIN=$1
CELL=$2
APPROOT=$3
FREEIPA_HOSTNAME=$4
TREADMILL_RELEASE=$5
LDAP_DC=ou=treadmill,$(echo "$DOMAIN" | sed -E 's/([a-z]*)\.([a-z]*)/dc=\1,dc=\2/g')
LDAP_URL=ldap://${FREEIPA_HOSTNAME}.${DOMAIN}:1389
ZK_URL=zookeeper://foo@TreadmillZookeeper1.${DOMAIN}:2181,TreadmillZookeeper2.${DOMAIN}:2181,TreadmillZookeeper3.${DOMAIN}:2181

curl -L "https://github.com/ThoughtWorksInc/treadmill/releases/download/${TREADMILL_RELEASE}/treadmill" -o /bin/treadmill

chmod +x /bin/treadmill

(
cat <<EOF
export TREADMILL_ZOOKEEPER=$ZK_URL
export TREADMILL_CELL=$CELL
export TREADMILL_APPROOT=$APPROOT
export TREADMILL_DNS_DOMAIN=$DOMAIN
export TREADMILL_LDAP=$LDAP_URL
export TREADMILL_LDAP_SEARCH_BASE=${LDAP_DC}
EOF
) >> /root/.bashrc
