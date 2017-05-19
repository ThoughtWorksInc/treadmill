#!/bin/bash -e

cd /home/treadmld

if [[ ! -d /home/treadmld/skalibs/.git ]]
	then
		git clone git://git.skarnet.org/skalibs
		cd skalibs && ./configure && make && sudo make install && cd -
fi

if [[ ! -d /home/treadmld/execline/.git ]]
	then
		git clone git://git.skarnet.org/execline
		cd execline && ./configure && make && sudo make install && cd -
fi

if [[ ! -d /home/treadmld/s6/.git ]]
	then
		git clone https://github.com/skarnet/s6.git
		cd s6 && ./configure && make && sudo make install && cd -
fi

cd -
