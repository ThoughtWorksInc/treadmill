Ensure route table exists:
  boto_vpc.route_table_present:
    - name: Treadmill-rtb
    - vpc_name: {{ pillar['vpc']['name'] }}
    - region: {{ pillar['vpc']['region'] }}
    - subnet_names:
      - {{ pillar['vpc']['subnet']['name'] }}
    - routes:
      - destination_cidr_block: 0.0.0.0/0
        internet_gateway_name: Treadmill-igw
    - keyid: {{ pillar['AWS_ACCESS_KEY_ID'] }}
    - key: {{ pillar['AWS_SECRET_ACCESS_KEY'] }}
