#!/bin/bash -e

SPOT_PRICE=$(/opt/treadmill/bin/treadmill cloud --domain treadmill.org spot-price)

if [ $(/bin/echo "$SPOT_PRICE > $DEMAND_PRICE" | /bin/bc) -eq 1 ] ; then
    /bin/echo "Spot price greater than demand price need to switch to on demand" | /bin/wall
fi
