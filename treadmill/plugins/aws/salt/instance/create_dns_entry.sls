myarecord:
  boto_route53.hosted_zone_present:
    - name: 'test.treadmill.'
    - vpc_name: {{ pillar['vpc']['name'] }}
    - vpc_region: {{ pillar['vpc']['region'] }}
    - region: {{ pillar['vpc']['region'] }}
    - private_zone: True
    - profile:
        keyid: {{ pillar['AWS_ACCESS_KEY_ID'] }}
        key: {{ pillar['AWS_SECRET_ACCESS_KEY'] }}
