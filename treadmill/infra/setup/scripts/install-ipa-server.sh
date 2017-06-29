yum install -y ipa-server

/sbin/ipa-server-install -U --domain "{{ DOMAIN }}" \
    --realm "{{ DOMAIN|upper }}" \
    -a "{{ IPA_ADMIN_PASSWORD }}" \
    -p "{{ IPA_ADMIN_PASSWORD }}"

