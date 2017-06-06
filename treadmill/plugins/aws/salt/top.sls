base:
  'master_minion':
    - vpc/create-vpc
    - vpc/create-subnet
    - vpc/create-igw
    - vpc/create-route
    - instance/create-instance
    - instance/create-security-group
  'freeipa':
    - instance/create-dns-entry
    - freeipa/configure
