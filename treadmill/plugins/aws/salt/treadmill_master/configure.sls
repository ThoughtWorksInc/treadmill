Install yum packages:
  pkg.installed:
    - pkgs:
      - zookeeper

/etc/hosts:
  file.append:
    - text:
      - {{ grains['ipv4'][1] }} {{ pillar['master']['name'] }}.{{ pillar['domain'] }}
