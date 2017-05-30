Install freeipa and openldap packages:
  pkg.installed:
    - pkgs:
      - ipa-server
      - openldap-servers

/etc/hosts:
  file.append:
    - text:
      - {{ grains.get('ipv4', 'not found >>>>>>>>>>>>')[1] }} {{ pillar['freeipa_server']['name'] }}1.{{ pillar['domain'] }}