Ensure VPC exists:
  boto_vpc.present:
    - name: salt_vpc
    - cidr_block: {{ pillar['vpc']['cidr'] }}
    - dns_hostnames: True
    - region: {{ pillar['vpc']['region'] }}
    - profile:
        keyid: {{ pillar['AWS_ACCESS_KEY_ID'] }}
        key: {{ pillar['AWS_SECRET_ACCESS_KEY'] }}