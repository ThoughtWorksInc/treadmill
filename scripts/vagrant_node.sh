#!/bin/bash

echo 'Installing treadmill node services dependencies'
yum install lvm2* ipset iptables bridge-utils libcgroup-tools conntrack-tools rrdtool-devel -y

echo 'node provisioned!'
