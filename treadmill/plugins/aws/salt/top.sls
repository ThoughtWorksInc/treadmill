base:
  'master_minion':
    - vpc/create-vpc
    - vpc/create-subnet
    - vpc/create-igw
    - vpc/create-route
    - instance
  'freeipa':
    - freeipa/configure
