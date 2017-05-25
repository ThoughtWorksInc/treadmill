Install freeipa and openldap packages:
  pkg.installed:
    - pkgs:
      - ipa-server
      - openldap-servers