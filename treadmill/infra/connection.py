import boto3


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        resource = kwargs.get(
            'resource',
            ('ec2' if (len(args) == 0) else args[0])
        )
        instance_resources = [klass._service_model.service_name.lower()
                              for klass in list(cls._instances.values())]
        if (resource.lower() not in instance_resources):
            cls._instances[cls] = super(
                Singleton, cls
            ).__call__(*args, **kwargs)
        return cls._instances[cls]


class Connection(metaclass=Singleton):
    def __init__(self, resource='ec2', region_name='us-east-1'):
        pass

    def __new__(cls, resource='ec2', region_name='us-east-1'):
        return boto3.client(resource, region_name=region_name)
