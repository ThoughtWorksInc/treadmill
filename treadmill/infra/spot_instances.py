from treadmill.infra import connection, instances, constants, subnet
from datetime import datetime, timedelta
import time
import base64
import polling


class SpotInstances(instances.Instances):

    @classmethod
    def get_current_spot_price(cls, instance_type):
        conn = connection.Connection()
        return float(conn.describe_spot_price_history(
            AvailabilityZone=subnet.Subnet._availability_zone(),
            InstanceTypes=[instance_type],
            StartTime=datetime.now(),
            EndTime=datetime.now(),
            Filters=[{
                'Name': 'product-description',
                'Values': ['Linux/UNIX']
            }]
        )['SpotPriceHistory'][0]['SpotPrice'])

    @classmethod
    def create(
            cls,
            name,
            key_name,
            count,
            image,
            instance_type,
            subnet_id,
            secgroup_ids,
            role,
            user_data
    ):
        launch_specifications = {
            'ImageId': SpotInstances.get_ami_id(image),
            'InstanceType': instance_type,
            'KeyName': key_name,
            'NetworkInterfaces': [{
                'DeviceIndex': 0,
                'SubnetId': subnet_id,
                'Groups': secgroup_ids,
                'AssociatePublicIpAddress': True
            }],
            'UserData': base64.b64encode(user_data.encode()).decode()
        }
        conn = connection.Connection()
        region = connection.Connection.context.region_name
        spot_requests = conn.request_spot_instances(
            SpotPrice=constants.DEMAND_PRICE[region],
            LaunchSpecification=launch_specifications,
            InstanceCount=count
        )['SpotInstanceRequests']

        conn = connection.Connection()

        def _wait_for_instance_id(spot_request_id, _instance):
            _req = conn.describe_spot_instance_requests(
                SpotInstanceRequestIds=[spot_request_id]
            )['SpotInstanceRequests'][0]
            _instance._id = _req.get('InstanceId')
            return _instance._id is not None

        _instances = SpotInstances(instances=[])
        for req in spot_requests:
            _instance = instances.Instance(id=None, name=name, role=role)
            spot_request_id = req['SpotInstanceRequestId']
            polling.poll(
                lambda: _wait_for_instance_id(spot_request_id, _instance),
                step=10,
                timeout=600
            )
            _instance.metadata = cls.load_json(ids=[_instance._id])[0]
            _instance.create_tags()
            _instances.instances.append(_instance)

    @classmethod
    def _get_average_price_for_one_hour(
        cls, availability_zone, product_description, instance_type
    ):
        conn = connection.Connection()
        _time = datetime.now()
        response = conn.describe_spot_price_history(
            StartTime=_time - timedelta(hours=1),
            EndTime=_time,
            ProductDescriptions=[product_description],
            AvailabilityZone=availability_zone,
            InstanceTypes=[instance_type]
        )

        spot_prices = [
            float(history['SpotPrice'])
            for history in response['SpotPriceHistory']
        ]

        return sum(spot_prices) / float(len(spot_prices))


