import boto3

def describe_auto_scaling_group(asGroupName):
	client = boto3.client('autoscaling')
	response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[asGroupName])
	group = response['AutoScalingGroups'][0]
	minSize = group['MinSize']
	desiredCapacity = group['DesiredCapacity']

	azInstanceIds = {}

	for elem in group['Instances']:
		if elem['AvailabilityZone'] not in azInstanceIds:
			azInstanceIds[elem['AvailabilityZone']] = []
		azInstanceIds[elem['AvailabilityZone']].append(elem['InstanceId'])

	return minSize, desiredCapacity, azInstanceIds

def terminate_instance(instanceId):
	client = boto3.client('autoscaling')
	response = client.terminate_instance_in_auto_scaling_group(
		InstanceId=instanceId,
		ShouldDecrementDesiredCapacity=True
	)
	return response
