#!/bin/bash -e

sudo mount --make-rprivate /

id -u treadmld &>/dev/null || useradd treadmld

export PYTHON_EGG_CACHE=/tmp/.python-eggs

echo 'Installing dependencies'
yum -y group install "Development Tools"
sudo yum install epel-release -y
sudo yum install git python-pip python34-devel openssl-devel libffi-devel -y
pip install virtualenv

echo 'Setting up S6'
/home/treadmld/treadmill/scripts/s6_setup.sh

cd /home/treadmld && virtualenv env -p python3
source env/bin/activate && cd -

cd /home/treadmld/treadmill
python setup.py develop
treadmill --help && cd -

echo 'compiling pid1'
cd /home/treadmld/treadmill-pid1 && make && cd -
