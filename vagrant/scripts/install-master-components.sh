#!/bin/sh

# Start root supervisor.

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

set -e

# Source environment variables.
SCRIPTDIR=$(cd $(dirname $0) && pwd)

source $SCRIPTDIR/env_vars.sh

. $SCRIPTDIR/svc_utils.sh

TM=/opt/treadmill/bin/treadmill

echo Installing openldap

del_svc openldap

echo Adding host to service keytab retrieval list

REQ_URL="http://ipa:8000/ipa/service"
REQ_STATUS=254
TIMEOUT_RETRY_COUNT=0
while [ $REQ_STATUS -eq 254 ] && [ $TIMEOUT_RETRY_COUNT -ne 30 ]
do
    REQ_OUTPUT=$(curl --connect-timeout 5 -H "Content-Type: application/json" -X POST -d '{"domain": "ms.local", "hostname": "'master.ms.local'", "service": "'ldap/master.ms.local'"}' "${REQ_URL}" 2>&1) && REQ_STATUS=0 || REQ_STATUS=254
    TIMEOUT_RETRY_COUNT=$((TIMEOUT_RETRY_COUNT+1))
    sleep 60
done

kinit -kt /etc/krb5.keytab

echo Retrieving ldap service keytab
ipa-getkeytab -s "ipa.ms.local" -p "ldap/master.ms.local@MS.LOCAL" -k /etc/ldap.keytab

ipa-getkeytab -r -p treadmld -D "cn=Directory Manager" -w "Tre@dmill1" -k /etc/treadmld.keytab
chown treadmld:treadmld /etc/ldap.keytab /etc/treadmld.keytab

su -c "kinit -kt /etc/treadmld.keytab treadmld" treadmld

/opt/s6/bin/s6-setuidgid treadmld \
    $TM admin install --install-dir /var/tmp/treadmill-openldap \
        openldap \
        --owner treadmld \
        --uri ldap://master.ms.local:22389 \
        --suffix dc=ms,dc=local \
        --gssapi

add_svc openldap

echo Initializing openldap
sleep 3

/opt/s6/bin/s6-setuidgid treadmld \
    $TM admin ldap init

(
# FIXME: Flaky command. Works after a few re-runs.
TIMEOUT=120

retry_count=0
until ( /opt/s6/bin/s6-setuidgid treadmld \
    $TM admin ldap schema --update ) || [ $retry_count -eq $TIMEOUT ]
do
    retry_count=`expr $retry_count + 1`
    echo "Trying ldap schema update : $retry_count"
    sleep 1
done
)

echo Configuring local cell

/opt/s6/bin/s6-setuidgid treadmld \
    $TM admin ldap cell configure local --version 0.1 --root /opt/treadmill \
        --username treadmld \
        --location local.local \

# For simplicity, use default zookeeper port - 2181. This way default
# install of zookeeper tools will just work.
#
# This is single node Zookeeper install, no need to specify additional
# ports.
/opt/s6/bin/s6-setuidgid treadmld \
    $TM admin ldap cell insert local --idx 1 --hostname master \
        --client-port 2181

# Add server to the cell.
/opt/s6/bin/s6-setuidgid treadmld \
    $TM admin ldap server configure node --cell local

echo Extracting cell config

$TM --outfmt yaml admin ldap cell configure local >/var/tmp/cell_conf.yml

echo Installing zookeper

del_svc zookeeper

/opt/s6/bin/s6-setuidgid treadmld \
    $TM admin install \
        --install-dir /var/tmp/treadmill-zookeeper \
        --config /var/tmp/cell_conf.yml \
        zookeeper \
        --master-id 1

add_svc zookeeper

echo Installing Treadmill Master

del_svc treadmill-master

$TM admin install \
    --install-dir /var/tmp/treadmill-master \
    --config /var/tmp/cell_conf.yml \
    master \
    --master-id 1 \
    --ldap-pwd secret

add_svc treadmill-master

touch /home/vagrant/.ssh/config
cat << EOF > /home/vagrant/.ssh/config
Host node
  IdentityFile ~/treadmill/vagrant/.vagrant/machines/node/virtualbox/private_key
EOF
chmod 600 /home/vagrant/.ssh/config
chown vagrant -R /home/vagrant/.ssh/config
