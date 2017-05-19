#!/bin/bash

treadmill sproc restapi -p 8000 --title 'Treadmill_Query_API' -m trace,state,endpoint --cors-origin='.*'
treadmill sproc restapi -p 8000 --title 'Treadmill_Cell_API' -m instance,app-monitor,identity-group,nodeinfo --cors-origin='.*'
treadmill sproc restapi -p 8000 --title 'Treadmill_Global_Config_API' -m app,app-group,app-dns,tenant,lbendpoint,allocation,cell --cors-origin='.*'
