#!/bin/bash -e

echo 'password' > /home/treadmld/.treadmill_ldap

echo 'Installing treadmill master services dependencies'
yum install java wget openldap-servers -y

echo 'Setting up Zookeeper'
/home/treadmld/treadmill/scripts/zk_setup.sh

sudo service slapd start

echo 'master provisioned!'
