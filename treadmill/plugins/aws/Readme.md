# Salt Vagrant Setup

In the current directory run the following to create salt master and minion VMs-
```sh
vagrant up
```

Current directory will be mounted to `/srv/` inside salt master.

Required aws configuration such as region can be changed in the pillar data(`/srv/pillar`)

Run the following to ssh into the salt master VM-

```sh
vagrant ssh salt_master
```

Salt Master also contains a minion on it to interact with aws to create vpc, subnet etc.

## Create VPC, Subnet, Gateway, EC2 instance

Become root user and export the AWS Credentials

```sh
sudo su -
export AWS_ACCESS_KEY_ID=<Access Key ID>
export AWS_SECRET_ACCESS_KEY=<Secret Access Key>
```
To create ec2 instances, `salt-cloud` package is used which takes the configuration from cloud.profiles and cloud.providers files present in `/srv/etc/`. Make the necessary changes.

Run salt command

```sh
salt '*' --batch-size=1 state.apply pillar='{AWS_ACCESS_KEY_ID: "'$AWS_ACCESS_KEY_ID'", AWS_SECRET_ACCESS_KEY: "'$AWS_SECRET_ACCESS_KEY'"}'
```
