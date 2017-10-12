from treadmill.infra import connection, instances
import time
import sys
import polling


instance_id = sys.argv[-1]


def create_image():
    conn = connection.Connection()
    return conn.create_image(
        InstanceId=instance_id,
        Name=instance_id + '-' + str(time.time()),
        NoReboot=True
    )['ImageId']


def create_on_demand_instance_for(image_id):
    _instances = instances.Instances.get(ids=[instance_id])
    spot_instance = _instances.instances[0]
    return instances.Instances.create(
        image_id=image_id,
        subnet_id=spot_instance.metadata['SubnetId'],
        key_name='ms_treadmill_dev',
        secgroup_ids=[sg['GroupId'] for sg in spot_instance.metadata['SecurityGroups']],
        instance_type=spot_instance.metadata['InstanceType'],
        count=1,
        user_data='su -c "kinit -k -t /etc/treadmld.keytab treadmld" treadmld && systemctl start treadmill-node',
        role='NODE',
        name=spot_instance.name,
        image=''
    )


def is_ami_available(ami_id):
    conn = connection.Connection()
    return conn.describe_images(ImageIds=[ami_id])['Images'][0]['State'] == 'available'


image_id = create_image()
polling.poll(
    lambda: is_ami_available(image_id),
    step=10,
    timeout=600
)
create_on_demand_instance_for(image_id)
