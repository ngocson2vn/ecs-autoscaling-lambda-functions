import boto3

def get_container_instances(clusterName, instanceStatus):
	client = boto3.client('ecs')

	response = client.list_container_instances(
		cluster=clusterName,
		status=instanceStatus
	)

	containerInstances = []
	if 'containerInstanceArns' in response:
		containerInstances = response["containerInstanceArns"]

	while True:
		if 'nextToken' in response:
			nextToken = response["nextToken"]
			response = client.list_container_instances(
				cluster=clusterName,
				nextToken=nextToken,
				status=instanceStatus
			)

			if 'containerInstanceArns' in response:
				containerInstances = containerInstances + response["containerInstanceArns"]
		else:
			break

	return containerInstances

def get_container_instance_id(instanceId, clusterName):
	client = boto3.client('ecs')
	containerInstances = get_container_instances(clusterName, 'ACTIVE')
	count = len(containerInstances)

	i = 0
	while i < count:
		response = client.describe_container_instances(
			cluster=clusterName,
			containerInstances=containerInstances[i:i+10]
		)
		for ci in response["containerInstances"]:
			if ci["ec2InstanceId"] == instanceId:
				return ci["containerInstanceArn"]
		i = i + 10

	return None


def get_drained_ec2instances(clusterName):
	client = boto3.client('ecs')
	containerInstances = get_container_instances(clusterName, 'DRAINING')

	instanceIds = []
	if len(containerInstances) > 0:
		response = client.describe_container_instances(
			cluster=clusterName,
			containerInstances=containerInstances
		)

		for ci in response["containerInstances"]:
			print "DRAINING: (ec2InstanceId: %s, runningTasksCount: %s)" % (ci["ec2InstanceId"], ci["runningTasksCount"])
			if ci["runningTasksCount"] == 0:
				instanceIds.append(ci["ec2InstanceId"])

	return instanceIds


def drain_container_instance(instanceId, clusterName):
	client = boto3.client('ecs')
	containerInstanceId = get_container_instance_id(instanceId, clusterName)
	if containerInstanceId:
		response = client.update_container_instances_state(
			cluster=clusterName,
			containerInstances=[
				containerInstanceId,
			],
			status='DRAINING'
		)
		if 'containerInstances' in response:
			print "Changed the state of (%s, %s) to DRAINING" % (instanceId, containerInstanceId)
