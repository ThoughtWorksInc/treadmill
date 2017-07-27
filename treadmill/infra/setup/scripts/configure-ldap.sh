echo Installing openldap

yum -y install openldap openldap-clients openldap-servers ipa-admintools

echo "{{ IPA_ADMIN_PASSWORD }}" | kinit admin
AMI_LAUNCH_INDEX=$(curl http://169.254.169.254/latest/meta-data/ami-launch-index)
ID=$((AMI_LAUNCH_INDEX+1))
INSTANCE_ID=$(curl http://169.254.169.254/latest/meta-data/instance-id)

ipa service-add --force "ldap/treadmillldap${ID}-${INSTANCE_ID}.{{ DOMAIN }}@{{ DOMAIN|upper }}"

echo Retrieving LDAP service keytab
ipa-getkeytab -p "ldap/treadmillldap${ID}-${INSTANCE_ID}.{{ DOMAIN }}" -D "cn=Directory Manager" -w "{{ IPA_ADMIN_PASSWORD }}" -k /etc/ldap.keytab
ipa-getkeytab -r -p treadmld -D "cn=Directory Manager" -w "{{ IPA_ADMIN_PASSWORD }}" -k /etc/treadmld.keytab
chown treadmld:treadmld /etc/ldap.keytab /etc/treadmld.keytab

# Enable 22389 port for LDAP (requires policycoreutils-python)
/sbin/semanage  port -a -t ldap_port_t -p tcp 22389
/sbin/semanage  port -a -t ldap_port_t -p udp 22389

setenforce 0
sed -i -e 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config

# Add openldap service
(
cat <<EOF
[Unit]
Description=OpenLDAP Directory Server
After=network.target

[Service]
Environment="KRB5_KTNAME=/etc/ldap.keytab"
User=treadmld
Group=treadmld
SyslogIdentifier=openldap
ExecStart=/var/tmp/treadmill-openldap/bin/run.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
) > /etc/systemd/system/openldap.service

s6-setuidgid treadmld \
    treadmill admin install --install-dir /var/tmp/treadmill-openldap \
        openldap \
        --owner treadmld \
        --uri ldap://0.0.0.0:22389 \
        --suffix "${LDAP_DC}" \
        --gssapi

# TODO: Create global utility function for adding service
systemctl daemon-reload
systemctl enable openldap.service --now

echo Initializing openldap

su -c "kinit -k -t /etc/treadmld.keytab treadmld" treadmld

s6-setuidgid treadmld \
    treadmill admin ldap init

s6-setuidgid treadmld \
    treadmill admin ldap schema --update

echo Configuring local cell

s6-setuidgid treadmld \
    treadmill admin ldap cell configure "{{ SUBNET_ID }}" --version 0.1 --root "{{ APP_ROOT }}" \
        --username treadmld \
        --location local.local
