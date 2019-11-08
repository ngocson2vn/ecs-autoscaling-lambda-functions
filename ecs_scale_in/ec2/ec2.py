import boto3
import pytz
import datetime


def get_oldest_instance(instanceIds):
	client = boto3.client('ec2')
	instDict=client.describe_instances(InstanceIds=instanceIds)
	launchTime = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=pytz.UTC)
	ipAddress = ''

	for r in instDict['Reservations']:
		for instance in r['Instances']:
			print instance['LaunchTime'], instance['PrivateIpAddress']
			if launchTime > instance['LaunchTime']:
				launchTime = instance['LaunchTime']
				instanceId = instance['InstanceId']
				ipAddress = instance['PrivateIpAddress']

	return instanceId, ipAddress


def create_tag(instanceId, tagKey, tagValue):
	client = boto3.client('ec2')
	client.create_tags(
		Resources=[
			instanceId,
		],
		Tags=[
			{
				'Key': tagKey,
				'Value': tagValue,
			},
		],
	)


def mark_instance_as_retiring(instanceId, clusterName):
	tagKey = 'AutoScalingState'
	tagValue = '%sECSRetiring' % clusterName
	create_tag(instanceId, tagKey, tagValue)
