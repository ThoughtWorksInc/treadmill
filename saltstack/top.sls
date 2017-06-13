base:
    'tm_role:freeipa':
        - match: grain
        - freeipa/configure
    'tm_role:SaltMaster':
        - match: grain
        - saltmaster/configure
