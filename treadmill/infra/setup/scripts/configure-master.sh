LDAP_DC=ou=treadmill,$(echo "{{ DOMAIN }}" | sed -E 's/([a-z]*)\.([a-z]*)/dc=\1,dc=\2/g')
LDAP_URL=ldap://{{ IPA_HOSTNAME }}.{{ DOMAIN }}:1389
ZK_URL=zookeeper://foo@TreadmillZookeeper1.{{ DOMAIN }}:2181,TreadmillZookeeper2.{{ DOMAIN }}:2181,TreadmillZookeeper3.{{ DOMAIN }}:2181
AMI_LAUNCH_INDEX=$(curl -s http://169.254.169.254/latest/meta-data/ami-launch-index)
MASTER_ID=$(expr $AMI_LAUNCH_INDEX + 1) # AMI_LAUNCH_INDEX is 0 indexed, master cannot be set to 0.

curl -L "https://github.com/ThoughtWorksInc/treadmill/releases/download/{{ TREADMILL_RELEASE }}/treadmill" -o /bin/treadmill

chmod +x /bin/treadmill

(
cat <<EOF
export TREADMILL_ZOOKEEPER=$ZK_URL
export TREADMILL_CELL={{ CELL }}
export TREADMILL_APPROOT={{ APPROOT }}
export TREADMILL_DNS_DOMAIN={{ DOMAIN }}
export TREADMILL_LDAP=$LDAP_URL
export TREADMILL_LDAP_SEARCH_BASE=${LDAP_DC}
EOF
) >> /root/.bashrc

# Start master service
. /root/.bashrc && nohup treadmill admin install --profile aws master --master-id ${MASTER_ID}  --run > master_services.out 2>&1 &
