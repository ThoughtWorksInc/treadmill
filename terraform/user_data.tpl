#!/bin/bash

curl -o bootstrap-salt.sh -L https://bootstrap.saltstack.com
sh bootstrap-salt.sh

salt-call --local grains.append tm_role "${role}"
curl -L "${tm_repo}/archive/${git_branch}.tar.gz" -o /tmp/treadmill.tar.gz
tar xvf /tmp/treadmill.tar.gz

salt-call --file-root="treadmill-${git_branch}/saltstack" --local state.apply
