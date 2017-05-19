#!/bin/bash

nohup treadmill sproc restapi -p 8000 --title 'Treadmill_Query_API' -m trace,state,endpoint --cors-origin='.*' > state_api.out 2>&1 &
nohup treadmill sproc restapi -p 8001 --title 'Treadmill_Cell_API' -m instance,app-monitor,identity-group,nodeinfo --cors-origin='.*' > cell_api.out 2>&1 &
nohup treadmill sproc restapi -p 8002 --title 'Treadmill_Global_Config_API' -m app,app-group,app-dns,tenant,lbendpoint,allocation,cell --cors-origin='.*' > admin_api.out 2>&1 &
