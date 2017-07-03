#install
yum install -y ipa-client

#configure
CLIENT_HOSTNAME=$(hostname)
CLIENT_IP=$(curl http://169.254.169.254/latest/meta-data/local-ipv4)

grep -F -q '$CLIENT_IP $CLIENT_HOSTNAME' /etc/hosts || echo $CLIENT_IP $CLIENT_HOSTNAME >> /etc/hosts
