base:
  'master_minion':
    - vpc/create-vpc
    - vpc/create-subnet
    - vpc/create-igw
    - vpc/create-route
    - instance/create-instance
  'freeipa':
    - instance/create-dns-entry
    - freeipa/configure
