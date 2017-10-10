from treadmill.infra import connection, instances, constants, subnet
from datetime import datetime, timedelta
import time
import base64


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

        for req in spot_requests:
            if req['State'] == 'active':
                _instance_id = req['InstanceId']
            else:
                _instance_id = cls._wait_for_request_fulfillment(req)
            _instance_metadata = cls.load_json(ids=[_instance_id])[0]
            _instance = instances.Instance(id=_instance_id, name=name,
                                           role=role,
                                           metadata=_instance_metadata)
            _instance.create_tags()

    @classmethod
    def _wait_for_request_fulfillment(cls, request):
        conn = connection.Connection()
        while True:
            time.sleep(30)
            request = conn.describe_spot_instance_requests(
                SpotInstanceRequestIds=[request['SpotInstanceRequestId']]
            )['SpotInstanceRequests'][0]
            if request['State'] == 'active':
                return request['InstanceId']

    @classmethod
    def _get_average_price_for_one_hour(
        cls, availability_zone, product_description, instance_type
    ):
        conn = connection.Connection()
        time = datetime.now()
        response = conn.describe_spot_price_history(
            StartTime=time - timedelta(hours=1),
            EndTime=time,
            ProductDescriptions=product_description,
            AvailabilityZone=availability_zone,
            InstanceTypes=[instance_type]
        )

        spot_prices = [
            history['SpotPrice']
            for history in response['SpotPriceHistory']
        ]

        return sum(spot_prices) / float(len(spot_prices))
