import os
import sys
import json
import datetime
import traceback

sys.path.append("./vendored")
from ecs import ecs
from cloudwatch import cloudwatch

ECS_CLUSTERS = [x.strip() for x in os.environ['ECS_CLUSTERS'].split(',')]

def publish_request_per_task(a, b):
	end_time = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(minutes=2)
	start_time = end_time - datetime.timedelta(minutes=1)

	for cluster in ECS_CLUSTERS:
		services = ecs.describe_services(cluster)

		for service in services:
			requestCountPerTarget = cloudwatch.get_request_count(service['targetGroup'], start_time, end_time)
			requestCountPerTask = requestCountPerTarget / service['desiredCount']			
			print "ServiceName: %s, RequestCountPerTarget: %s, DesiredCount: %s, RequestCountPerTask: %s" % (service['serviceName'], requestCountPerTarget, service['desiredCount'], requestCountPerTask)
			cloudwatch.publish_custom_metric('ServiceName', service['serviceName'], 'RequestCountPerTask', requestCountPerTask, 'None', start_time)
