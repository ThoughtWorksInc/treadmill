Ensure Subnet Exists:
  boto_vpc.subnet_present:
    - name: {{ pillar['vpc']['subnet']['name'] }}
    - cidr_block: {{ pillar['vpc']['subnet']['cidr'] }}
    - availability_zone: {{ pillar['vpc']['subnet']['az']}}
    - vpc_name: {{ pillar['vpc']['name'] }}
    - region: {{ pillar['vpc']['region'] }}
    - profile:
        keyid: {{ pillar['AWS_ACCESS_KEY_ID'] }}
        key: {{ pillar['AWS_SECRET_ACCESS_KEY'] }}