treadmill admin master app schedule --env prod --proid treadmld --manifest {{ MANIFEST_PATH }}/cellapi.yml treadmld.cellapi
treadmill admin master app schedule --env prod --proid treadmld --manifest {{ MANIFEST_PATH }}/adminapi.yml treadmld.adminapi
treadmill admin master app schedule --env prod --proid treadmld --manifest {{ MANIFEST_PATH }}/stateapi.yml treadmld.stateapi
