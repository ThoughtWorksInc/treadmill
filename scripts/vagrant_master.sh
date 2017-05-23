#!/bin/bash -e
TREADMILL_CODE="/home/treadmld/treadmill/"

echo 'password' > /home/treadmld/.treadmill_ldap

echo 'Installing treadmill master services dependencies'
yum install java wget openldap-servers -y

echo 'Setting up Zookeeper'
/home/treadmld/treadmill/scripts/zk_setup.sh

cp $TREADMILL_CODE"etc/ldap/treadmill.ldif" "/etc/openldap/slapd.d/cn=config/cn=schema/cn={1}treadmill.ldif"
chown ldap:ldap "/etc/openldap/slapd.d/cn=config/cn=schema/cn={1}treadmill.ldif"
chmod 0600 "/etc/openldap/slapd.d/cn=config/cn=schema/cn={1}treadmill.ldif"

cp $TREADMILL_CODE"etc/ldap/config.ldif" "/etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif"
chown ldap:ldap "/etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif"
chmod 0600 "/etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif"

cp $TREADMILL_CODE"etc/ldap/hdb.ldif" "/etc/openldap/slapd.d/cn=config/olcDatabase={2}hdb.ldif"
chown ldap:ldap "/etc/openldap/slapd.d/cn=config/olcDatabase={2}hdb.ldif"
chmod 0600 "/etc/openldap/slapd.d/cn=config/olcDatabase={2}hdb.ldif"

cp $TREADMILL_CODE"etc/ldap/slapd" "/etc/sysconfig/slapd"
chown root:root "/etc/sysconfig/slapd"
chmod 0644 "/etc/sysconfig/slapd"

chown -R ldap:ldap /var/lib/ldap

# Set nis_enabled selinux boolean
setsebool -P nis_enabled on

sudo service slapd start

# Make pid1 and put it in /bin/
cd $TREADMILL_CODE"../treadmill-pid1"
make
cp pid1 /bin
cd -

echo 'master provisioned!'
