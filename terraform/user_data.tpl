#!/bin/bash

curl -o bootstrap-salt.sh -L https://bootstrap.saltstack.com
sh bootstrap-salt.sh

salt-call --local grains.append tm_role "${role}"
curl -L https://github.com/ThoughtWorksInc/treadmill/archive/terraform_spike.tar.gz -o /tmp/treadmill.tar.gz

tar xvf /tmp/treadmill.tar.gz

salt-call --states-dir=treadmill-terraform_spike/saltstack --local state.apply
