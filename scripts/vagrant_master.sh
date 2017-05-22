#!/bin/bash -e

echo 'password' > /home/treadmld/.treadmill_ldap

echo 'Installing treadmill master services dependencies'
yum install java wget openldap-servers -y

echo 'Setting up Zookeeper'
/home/treadmld/treadmill/scripts/zk_setup.sh

cp "etc/ldap/treadmill.ldif" "/etc/openldap/slapd.d/cn=config/cn=schema/cn={1}treadmill.ldif"
chown ldap:ldap "/etc/openldap/slapd.d/cn=config/cn=schema/cn={1}treadmill.ldif"
chmod 0600 "/etc/openldap/slapd.d/cn=config/cn=schema/cn={1}treadmill.ldif"

cp "etc/ldap/config.ldif" "/etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif"
chown ldap:ldap "/etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif"
chmod 0600 "/etc/openldap/slapd.d/cn=config/olcDatabase={0}config.ldif"

cp "etc/ldap/hdb.ldif" "/etc/openldap/slapd.d/cn=config/olcDatabase={2}hdb.ldif"
chown ldap:ldap "/etc/openldap/slapd.d/cn=config/olcDatabase={2}hdb.ldif"
chmod 0600 "/etc/openldap/slapd.d/cn=config/olcDatabase={2}hdb.ldif"

cp "etc/ldap/slapd" "/etc/sysconfig/slapd"
chown root:root "/etc/sysconfig/slapd"
chmod 0644 "/etc/sysconfig/slapd"

chown -R ldap /var/lib/ldap
chgrp -R ldap /var/lib/ldap

sudo service slapd start

treadmill admin ldap init master
treadmill admin ldap schema --load treadmill/etc/ldap/schema.yml
treadmill admin ldap cell configure -u admin local

echo 'master provisioned!'
