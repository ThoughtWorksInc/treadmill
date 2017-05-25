#!/bin/bash
yum install epel-release -y
yum install salt-master -y
sed -i 's/#auto_accept: False/auto_accept: True/g' /etc/salt/master
salt-master -d