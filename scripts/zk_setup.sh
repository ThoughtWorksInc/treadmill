#!/bin/bash -e

cd /home/treadmld

wget -nc http://apache.claz.org/zookeeper/stable/zookeeper-3.4.10.tar.gz 
tar --skip-old-files -xvzf zookeeper-3.4.10.tar.gz
cp -n zookeeper-3.4.10/conf/zoo_sample.cfg zookeeper-3.4.10/conf/zoo.cfg
zookeeper-3.4.10/bin/zkServer.sh start
zookeeper-3.4.10/bin/zkServer.sh status
# env vars
grep -q -F 'source /home/treadmld/treadmill/scripts/env_vars.sh' ~/.bash_profile || echo 'source /home/treadmld/treadmill/scripts/env_vars.sh' >> ~/.bash_profile

cd -
