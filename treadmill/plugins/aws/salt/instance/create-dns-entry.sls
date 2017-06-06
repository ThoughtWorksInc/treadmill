Create Hosted Zone:
  boto_route53.hosted_zone_present:
    - name: {{ pillar['hosted_zone_name'] }}
    - domain_name: {{ pillar['hosted_zone_name'] }}.{{ pillar['domain'] }}
    - vpc_name: {{ pillar['vpc']['name'] }}
    - vpc_region: {{ pillar['vpc']['region'] }}
    - region: {{ pillar['vpc']['region'] }}
    - private_zone: True
    - profile:
        keyid: {{ pillar['AWS_ACCESS_KEY_ID'] }}
        key: {{ pillar['AWS_SECRET_ACCESS_KEY'] }}

Add entry to route53:
  boto_route53.present:
    - name: {{ grains['host']}}.{{ pillar['hosted_zone_name'] }}.{{ pillar['domain'] }}
    - value: {{ grains['ipv4'][1] }}
    - zone: {{ pillar['hosted_zone_name'] }}.{{ pillar['domain'] }}
    - ttl: 60
    - record_type: A
    - region: {{ pillar['vpc']['region'] }}
    - profile:
        keyid: {{ pillar['AWS_ACCESS_KEY_ID'] }}
        key: {{ pillar['AWS_SECRET_ACCESS_KEY'] }}
