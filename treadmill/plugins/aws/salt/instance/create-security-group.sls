Ensure security group exists:
  boto_secgroup.present:
    - name: {{ pillar['vpc']['sg_name'] }}
    - description: Treadmill security group
    - rules:
      - ip_protocol: tcp
        from_port: 22
        to_port: 22
        cidr_ip:
          - 0.0.0.0/0
      - ip_protocol: all
        source_group_name: {{ pillar['vpc']['sg_name'] }}
    - profile:
        keyid: {{ pillar['AWS_ACCESS_KEY_ID'] }}
        key: {{ pillar['AWS_SECRET_ACCESS_KEY'] }}