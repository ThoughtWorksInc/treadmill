#!/bin/bash
yum install epel-release -y
yum install salt-minion -y
echo "master: ${master_ip}" > /etc/salt/minion
salt-minion -d
