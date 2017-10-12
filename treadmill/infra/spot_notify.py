import subprocess
import sys
import json

while True:
    _output = subprocess.check_output([
        'treadmill',
        'admin',
        'cloud',
        '--domain',
        'treadmill.org',
        'spot-price'
    ]).decode('utf-8').replace("'", '"')
    _output = json.loads(_output)
    if _output['SpotPrice'] > float(_output['OnDemandPrice']):
        yes = set(['yes', 'y', 'Y'])
        print('On-Demand Price:', '$', float(_output['OnDemandPrice']))
        print('Current Spot Price:', '$', float(_output['SpotPrice']))
        print('Instance will be terminated.')
        _input = input('Switch to On-Demand [Y/n]?')
        if _input.lower() in yes:
            _instance_id = input('To confirm, enter instance-id:')
            subprocess.check_output([
                'python',
                '/home/vagrant/treadmill/treadmill/infra/setup/spot_to_on_demand.py',
                _instance_id
            ])
            sys.exit(0)
        else:
            print('You chose not to Switch to On-Demand. \
            Spot Instance will be stopped in few minutes.')
    elif _output['SpotPrice'] == float(_output['OnDemandPrice']):
        print('SpotPrice is equal to on-Demand price, can switch manually!')
    else:
        print(
            'Still saving:',
            '$',
            float(_output['OnDemandPrice']) - _output['SpotPrice'],
            '/ hour'
        )
