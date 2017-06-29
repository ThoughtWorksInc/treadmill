# install
yum clean all
rpm -ivh https://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-9.noarch.rpm
yum -y install python34

# Configure
AMI_LAUNCH_INDEX=$(curl http://169.254.169.254/latest/meta-data/ami-launch-index)
ID=$((AMI_LAUNCH_INDEX+1))

hostnamectl set-hostname "{{ NAME }}${ID}.{{ DOMAIN }}"

grep -q -F 'preserve_hostname: true' /etc/cloud/cloud.cfg || echo 'preserve_hostname: true' >> /etc/cloud/cloud.cfg
