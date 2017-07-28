echo Installing Node packages
yum -y install conntrack-tools iproute libcgroup libcgroup-tools bridge-utils openldap-clients

mkdir -p /opt/treadmill-pid1/bin
mkdir -p /opt/s6/bin
mkdir -p /opt/treadmill/bin
cp -p /bin/pid1 /opt/treadmill-pid1/bin/pid1
cp -p /bin/s6-* /opt/s6/bin/
cp -p /bin/treadmill /opt/treadmill/bin/

. /root/.bashrc

kinit -k

(
TIMEOUT=30
retry_count=0
until ( ldapsearch -c -H $TREADMILL_LDAP "ou=cells" ) || [ $retry_count -eq $TIMEOUT ]
do
    retry_count=$(($retry_count+1))
    sleep 30
done
)

treadmill --outfmt yaml admin ldap cell configure "{{ SUBNET_ID }}" > {{ APP_ROOT }}/cell_conf.yml

(
cat <<EOF
mkdir -p /var/spool/tickets
kinit -k -t /etc/krb5.keytab -c /var/spool/tickets/treadmld
chown treadmld:treadmld /var/spool/tickets/treadmld
EOF
) > /etc/cron.hourly/hostkey-treadmld-kinit

chmod 755 /etc/cron.hourly/hostkey-treadmld-kinit
/etc/cron.hourly/hostkey-treadmld-kinit

(
cat <<EOF
[Unit]
Description=Treadmill node services
After=network.target

[Service]
User=root
Group=root
SyslogIdentifier=treadmill
ExecStartPre=/bin/mount --make-rprivate /
ExecStart={{ APP_ROOT }}/treadmill-node/bin/run.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
) > /etc/systemd/system/treadmill-node.service

treadmill admin install \
    --install-dir {{ APP_ROOT }}/treadmill-node \
    --config {{ APP_ROOT }}/cell_conf.yml \
    node

/bin/systemctl daemon-reload
/bin/systemctl enable treadmill-node.service --now


echo "{{ IPA_ADMIN_PASSWORD }}" | kinit admin
ipa-getkeytab -r -p treadmld -D "cn=Directory Manager" -w "{{ IPA_ADMIN_PASSWORD }}" -k /etc/treadmld.keytab
chown treadmld:treadmld /etc/treadmld.keytab
su -c "kinit -k -t /etc/treadmld.keytab treadmld" treadmld

s6-setuidgid treadmld treadmill admin ldap server configure "$(hostname -f)" --cell "{{ SUBNET_ID }}"
