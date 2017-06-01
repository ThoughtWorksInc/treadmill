base:
  'master_minion':
    - vpc/create-vpc
    - vpc/create-subnet
    - vpc/create-igw
    - vpc/create-route
    - instance/create_instance
  'freeipa':
    - instance/create_dns_entry
    - freeipa/configure
