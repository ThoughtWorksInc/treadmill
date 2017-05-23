Create Internet Gateway:
  boto_vpc.internet_gateway_present:
    - name: Treadmill-igw
    - vpc_name: {{ pillar['vpc']['name'] }}
    - profile:
        keyid: {{ pillar['AWS_ACCESS_KEY_ID'] }}
        key: {{ pillar['AWS_SECRET_ACCESS_KEY'] }}
    - region: {{ pillar['vpc']['region'] }}