(
cat <<EOF
memory: 1G
cpu: 20%
disk: 1G
services:
- command: |
    exec treadmill sproc restapi -p 8000 \
      --title 'Treadmill_Cell_API' \
      -m instance,app-monitor,identity-group,nodeinfo --cors-origin='.*'
  name: rest-api
  restart:
    limit: 5
    interval: 60
endpoints:
- name: http
  port: 8000
  type: infra
EOF
) > /var/tmp/cellapi.yml

(
cat <<EOF
memory: 1G
cpu: 20%
disk: 1G
services:
- command: |
    exec treadmill sproc restapi -p 8000 \
      --title 'Treadmill_Global_Config_API' \
      -m app,app-group,app-dns,tenant,lbendpoint,allocation,cell \
      --cors-origin='.*'
  name: rest-api
  restart:
    limit: 5
    interval: 60
endpoints:
- name: http
  port: 8000
  type: infra
EOF
) > /var/tmp/adminapi.yml

(
cat <<EOF
memory: 1G
cpu: 20%
disk: 1G
services:
- command: |
    exec treadmill sproc restapi -p 8000 --title 'Treadmill_Query_API' \
      -m trace,state,endpoint --cors-origin='.*'
  name: state-api
  restart:
    limit: 5
    interval: 60
endpoints:
- name: http
  port: 8000
  type: infra
EOF
) > /var/tmp/stateapi.yml

{{ TREADMILL }} admin master app schedule --env prod --proid treadmld --manifest /var/tmp/cellapi.yml treadmld.cellapi
{{ TREADMILL }} admin master app schedule --env prod --proid treadmld --manifest /var/tmp/adminapi.yml treadmld.adminapi
{{ TREADMILL }} admin master app schedule --env prod --proid treadmld --manifest /var/tmp/stateapi.yml treadmld.stateapi
