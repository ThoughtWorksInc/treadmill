/etc/salt/cloud.profiles:
  file.symlink:
    - target: /srv/etc/cloud.profiles
    - user: vagrant

/etc/salt/cloud.providers:
  file.symlink:
    - target: /srv/etc/cloud.providers
    - user: vagrant

Create ec2 Instance:
  cmd.run:
    - name: salt-cloud --profile={{ pillar['profile'] }} {{ pillar['instance_name'] }}
    - cwd: /srv/
