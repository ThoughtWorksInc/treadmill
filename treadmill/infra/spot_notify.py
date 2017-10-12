import subprocess
import sys

while True:
    _output = subprocess.check_output([
        'treadmill',
        'cloud',
        '--domain',
        'treadmill.org',
        'spot-price'
    ])
    if _output['SpotPrice'] > float(_output['OnDemandPrice']):
        print('Time to switch to onDemand!')
        yes = set(['yes', 'y', 'Y'])
        _input = input('Switch to On-Demand [Y/n]?')
        if _input.lower() in yes:
            _instance_id = input('To confirm, enter instance-id:')
            subprocess.check_output([
                'python',
                './setup/spot_to_on_demand.py',
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
            '$'
            (float(_output['OnDemandPrice']) - _output['SpotPrice']),
            '/ hour'
        )
