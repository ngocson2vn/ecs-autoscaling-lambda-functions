import os
import sys
import datetime

sys.path.append("./vendored")
from ec2 import ec2
from ecs import ecs
from autoscaling import autoscaling
from cloudwatch import cloudwatch

ECS_CLUSTERS = [x.strip() for x in os.environ['ECS_CLUSTERS'].split(',')]
SCALE_IN_THRESHOLD = int(os.environ['SCALE_IN_THRESHOLD'])
DATAPOINT_PERIOD = int(os.environ['DATAPOINT_PERIOD'])
DATAPOINT_COUNT = int(os.environ['DATAPOINT_COUNT'])


def get_datapoints(clusterName, asGroupName):
	endTime = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(minutes=1)
	startTime = endTime - datetime.timedelta(minutes=DATAPOINT_PERIOD)
	datapoints = []

	for i in xrange(1, DATAPOINT_COUNT + 1):
		metricValue = cloudwatch.get_cluster_metric_value(clusterName, 'CPUMemoryUtilizationNormalized', startTime, endTime)
		print 'StartTime: %s, EndTime: %s, CPUMemoryUtilizationNormalized: %s' % (startTime, endTime, metricValue)

		if metricValue is not None and metricValue < SCALE_IN_THRESHOLD:
			datapoints.append(metricValue)

		endTime = startTime
		startTime = endTime - datetime.timedelta(minutes=DATAPOINT_PERIOD)

	return datapoints


def drain_ec2instance(event, context):
	IGNORE_UTC_HOUR_START = int(os.environ['IGNORE_UTC_HOUR_START'])
	IGNORE_UTC_HOUR_END = int(os.environ['IGNORE_UTC_HOUR_END'])
	currentHour = datetime.datetime.utcnow().hour

	if (IGNORE_UTC_HOUR_START <= currentHour) and (currentHour <= IGNORE_UTC_HOUR_END):
		return {'message': 'In ignore hours'}

	print "Current UTC hour: %d" % currentHour

	for clusterName in ECS_CLUSTERS:
		asGroupName = '%sECSAutoScaleGroup' % clusterName
		print "clusterName: %s, asGroupName: %s" % (clusterName, asGroupName)

		minSize, desiredCapacity, azInstanceIds = autoscaling.describe_auto_scaling_group(asGroupName)
		datapoints = get_datapoints(clusterName, asGroupName)
		if (len(datapoints) < DATAPOINT_COUNT) or (desiredCapacity == minSize):
			print "The scale-in conditions are not satisfied."
			continue

		# Get AZ with maximum instance count
		count = 0
		az = ''
		for key in azInstanceIds.keys():
			if len(azInstanceIds[key]) > count:
				count = len(azInstanceIds[key])
				az = key

		instanceId, ipAddress = ec2.get_oldest_instance(azInstanceIds[az])
		print "The oldest instance: (%s, %s)" % (instanceId, ipAddress)

		# Drain the oldest instance
		ecs.drain_container_instance(instanceId, clusterName)
	
	return {'message': 'OK'}


def terminate_drained_ec2instances(event, context):
	for clusterName in ECS_CLUSTERS:
		asGroupName = '%sECSAutoScaleGroup' % clusterName
		print "clusterName: %s, asGroupName: %s" % (clusterName, asGroupName)

		instanceIds = ecs.get_drained_ec2instances(clusterName)
		for instanceId in instanceIds:
			response = autoscaling.terminate_instance(instanceId)
			if 'Activity' in response:
				print "Terminated %s in %s." % (instanceId, response['Activity']['AutoScalingGroupName'])

	return {'message': 'OK'}
